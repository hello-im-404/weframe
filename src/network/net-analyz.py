#!/usr/bin/env python3

import pyshark
from collections import Counter, defaultdict
import ipaddress
import sys
import argparse
import json
import logging
import hashlib
import sqlite3
from datetime import datetime, timedelta
import asyncio
import aiohttp
from typing import Dict, List, Tuple, Optional
import configparser
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import re
import geoip2.database
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import os
import tempfile
import zipfile
from cryptography.fernet import Fernet
import hmac

# Дополнительные импорты для новых функций
import requests
from urllib.parse import urlparse
import socket
import subprocess
import statistics

# Enterprise конфигурация
class EnterpriseConfig:
    def __init__(self, config_file="enterprise_config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
    def get_siem_settings(self):
        return dict(self.config['SIEM']) if 'SIEM' in self.config else {}
    
    def get_alert_thresholds(self):
        return dict(self.config['ALERTS']) if 'ALERTS' in self.config else {}
    
    def get_email_settings(self):
        return dict(self.config['EMAIL']) if 'EMAIL' in self.config else {}
    
    def get_virustotal_settings(self):
        return dict(self.config['VIRUSTOTAL']) if 'VIRUSTOTAL' in self.config else {}
    
    def get_quarantine_settings(self):
        return dict(self.config['QUARANTINE']) if 'QUARANTINE' in self.config else {}

# Менеджер IOC с поддержкой TLP (Traffic Light Protocol)
class IOCManager:
    def __init__(self):
        self.malicious_ips = set()
        self.suspicious_domains = set()
        self.malware_hashes = set()
        self.ioc_metadata = {}  # TLP маркировки и источники
        
    def load_from_file(self, ioc_file: str):
        try:
            with open(ioc_file, 'r') as f:
                data = json.load(f)
                self.malicious_ips.update(data.get('malicious_ips', []))
                self.suspicious_domains.update(data.get('suspicious_domains', []))
                self.malware_hashes.update(data.get('malware_hashes', []))
                self.ioc_metadata = data.get('metadata', {})
        except Exception as e:
            logging.error(f"Error loading IOC file: {e}")
    
    def check_ip(self, ip: str) -> Tuple[bool, dict]:
        if ip in self.malicious_ips:
            return True, {'source': 'local_ioc', 'tlp': 'RED', 'confidence': 'high'}
        return False, {}
    
    def check_domain(self, domain: str) -> Tuple[bool, dict]:
        for suspicious in self.suspicious_domains:
            if suspicious in domain:
                return True, {'source': 'local_ioc', 'tlp': 'AMBER', 'confidence': 'medium'}
        return False, {}

# Интеграция с VirusTotal API
class VirusTotalIntegration:
    def __init__(self, config: EnterpriseConfig):
        self.config = config
        self.vt_settings = config.get_virustotal_settings()
        self.api_key = self.vt_settings.get('api_key', '')
        self.base_url = "https://www.virustotal.com/api/v3"
        
    async def check_ip_reputation(self, ip: str) -> Optional[Dict]:
        if not self.api_key:
            return None
            
        try:
            headers = {'x-apikey': self.api_key}
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/ip_addresses/{ip}", 
                                     headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logging.warning(f"VirusTotal API error: {response.status}")
        except Exception as e:
            logging.error(f"VirusTotal check failed: {e}")
        return None
    
    async def check_domain_reputation(self, domain: str) -> Optional[Dict]:
        if not self.api_key:
            return None
            
        try:
            headers = {'x-apikey': self.api_key}
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/domains/{domain}", 
                                     headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            logging.error(f"VirusTotal domain check failed: {e}")
        return None

# Система карантина для подозрительных файлов
class QuarantineSystem:
    def __init__(self, config: EnterpriseConfig):
        self.config = config
        self.quarantine_settings = config.get_quarantine_settings()
        self.quarantine_dir = self.quarantine_settings.get('quarantine_directory', '/tmp/quarantine')
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Создание карантинной директории
        os.makedirs(self.quarantine_dir, exist_ok=True)
    
    def quarantine_file(self, file_path: str, reason: str, metadata: Dict):
        """Помещение файла в карантин с шифрованием"""
        try:
            # Чтение и шифрование файла
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = self.cipher_suite.encrypt(file_data)
            
            # Создание метаданных карантина
            quarantine_id = hashlib.sha256(f"{file_path}{datetime.now()}".encode()).hexdigest()[:16]
            quarantine_file = os.path.join(self.quarantine_dir, f"{quarantine_id}.quarantine")
            
            quarantine_meta = {
                'original_path': file_path,
                'quarantine_date': datetime.now().isoformat(),
                'reason': reason,
                'original_size': len(file_data),
                'metadata': metadata,
                'quarantine_id': quarantine_id
            }
            
            # Сохранение зашифрованного файла и метаданных
            with open(quarantine_file, 'wb') as f:
                f.write(encrypted_data)
            
            meta_file = os.path.join(self.quarantine_dir, f"{quarantine_id}.meta")
            with open(meta_file, 'w') as f:
                json.dump(quarantine_meta, f, indent=2)
            
            # Удаление оригинального файла
            os.remove(file_path)
            
            logging.info(f"File quarantined: {file_path} -> {quarantine_id}")
            return quarantine_id
            
        except Exception as e:
            logging.error(f"Quarantine failed: {e}")
            return None

# Анализатор поведения сети (Behavioral Analysis)
class BehavioralAnalyzer:
    def __init__(self):
        self.baseline_established = False
        self.network_baseline = {}
        
    def establish_baseline(self, packets: List, window_size: int = 1000):
        """Установка базового профиля сетевого поведения"""
        if len(packets) < window_size:
            return
            
        protocols = []
        packet_sizes = []
        time_deltas = []
        
        for i, packet in enumerate(packets[:window_size]):
            protocols.append(packet.highest_layer)
            if hasattr(packet, 'length'):
                packet_sizes.append(int(packet.length))
            
            if i > 0 and hasattr(packet, 'sniff_time'):
                prev_time = packets[i-1].sniff_time
                curr_time = packet.sniff_time
                delta = (curr_time - prev_time).total_seconds()
                time_deltas.append(delta)
        
        self.network_baseline = {
            'protocol_distribution': dict(Counter(protocols)),
            'avg_packet_size': statistics.mean(packet_sizes) if packet_sizes else 0,
            'std_packet_size': statistics.stdev(packet_sizes) if len(packet_sizes) > 1 else 0,
            'avg_time_delta': statistics.mean(time_deltas) if time_deltas else 0,
            'std_time_delta': statistics.stdev(time_deltas) if len(time_deltas) > 1 else 0
        }
        self.baseline_established = True
        
    def detect_anomalies(self, packets: List) -> List[Dict]:
        """Обнаружение аномалий на основе базового профиля"""
        if not self.baseline_established:
            return []
            
        anomalies = []
        
        # Анализ последних пакетов
        recent_packets = packets[-500:]  # Последние 500 пакетов
        recent_sizes = [int(p.length) for p in recent_packets if hasattr(p, 'length')]
        
        if recent_sizes:
            avg_recent_size = statistics.mean(recent_sizes)
            baseline_avg = self.network_baseline['avg_packet_size']
            baseline_std = self.network_baseline['std_packet_size']
            
            # Обнаружение аномального размера пакетов
            if abs(avg_recent_size - baseline_avg) > 2 * baseline_std:
                anomalies.append({
                    'type': 'SIZE_ANOMALY',
                    'severity': 'MEDIUM',
                    'description': f'Average packet size anomaly: {avg_recent_size:.2f} vs baseline {baseline_avg:.2f}',
                    'deviation': abs(avg_recent_size - baseline_avg) / baseline_std
                })
        
        return anomalies

# Расширенный анализатор угроз с интеграцией VirusTotal
class AdvancedThreatAnalyzer(ThreatAnalyzer):
    def __init__(self, config: EnterpriseConfig):
        super().__init__(config)
        self.vt_integration = VirusTotalIntegration(config)
        self.behavioral_analyzer = BehavioralAnalyzer()
        self.suspicious_ports = {21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 
                               993, 995, 1723, 3306, 3389, 5900, 8080}
        
    async def analyze_packet_threats_advanced(self, packet) -> Dict:
        """Расширенный анализ угроз с интеграцией внешних источников"""
        threats = await super().analyze_packet_threats(packet)
        
        # Проверка подозрительных портов
        if 'TCP' in packet:
            try:
                dst_port = int(packet.tcp.dstport)
                if dst_port in self.suspicious_ports:
                    threats.append({
                        'type': 'SUSPICIOUS_PORT',
                        'port': dst_port,
                        'severity': 'LOW',
                        'description': f'Communication on suspicious port {dst_port}'
                    })
            except (AttributeError, ValueError):
                pass
        
        # Проверка через VirusTotal для внешних IP
        if 'IP' in packet and not self.is_local_ip(packet.ip.src):
            vt_result = await self.vt_integration.check_ip_reputation(packet.ip.src)
            if vt_result and 'data' in vt_result:
                stats = vt_result['data']['attributes'].get('last_analysis_stats', {})
                malicious_count = stats.get('malicious', 0)
                
                if malicious_count > 0:
                    threats.append({
                        'type': 'VT_MALICIOUS_IP',
                        'ip': packet.ip.src,
                        'malicious_engines': malicious_count,
                        'total_engines': sum(stats.values()),
                        'severity': 'HIGH' if malicious_count > 5 else 'MEDIUM'
                    })
        
        return threats
    
    def detect_data_exfiltration(self, packets: List) -> List[Dict]:
        """Обнаружение потенциальной эксфильтрации данных"""
        exfiltration_signs = []
        dns_tunneling_candidates = []
        
        for packet in packets:
            # Обнаружение DNS туннелирования
            if 'DNS' in packet and hasattr(packet.dns, 'qry_name'):
                domain = packet.dns.qry_name
                # Подозрительные длинные DNS запросы
                if len(domain) > 100:
                    dns_tunneling_candidates.append({
                        'domain': domain,
                        'length': len(domain),
                        'packet_time': getattr(packet, 'sniff_time', datetime.now())
                    })
        
        if dns_tunneling_candidates:
            exfiltration_signs.append({
                'type': 'DNS_TUNNELING_SUSPICION',
                'severity': 'HIGH',
                'candidates': dns_tunneling_candidates[:10],  # Ограничение вывода
                'total_suspicious': len(dns_tunneling_candidates)
            })
        
        return exfiltration_signs

# Система отчетов в форматах STIX/TAXII
class STIXReportGenerator:
    def __init__(self):
        self.stix_version = "2.1"
    
    def generate_stix_bundle(self, threats: List[Dict], metadata: Dict) -> Dict:
        """Генерация отчета в формате STIX 2.1"""
        bundle = {
            "type": "bundle",
            "id": f"bundle--{hashlib.md5(str(datetime.now()).encode()).hexdigest()}",
            "spec_version": self.stix_version,
            "objects": []
        }
        
        for threat in threats:
            # Создание объекта Indicator для каждой угрозы
            indicator = {
                "type": "indicator",
                "id": f"indicator--{hashlib.md5(str(threat).encode()).hexdigest()}",
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "pattern": self._create_stix_pattern(threat),
                "pattern_type": "stix",
                "valid_from": datetime.now().isoformat(),
                "labels": ["malicious-activity"],
                "name": f"Threat: {threat.get('type', 'Unknown')}",
                "description": f"Detected threat: {threat}"
            }
            bundle["objects"].append(indicator)
        
        return bundle
    
    def _create_stix_pattern(self, threat: Dict) -> str:
        """Создание STIX паттерна для угрозы"""
        if 'ip' in threat:
            return f"[ipv4-addr:value = '{threat['ip']}']"
        elif 'domain' in threat:
            return f"[domain-name:value = '{threat['domain']}']"
        else:
            return "[threat:value = 'unknown']"

# Расширенный класс основного анализатора
class AdvancedEnterpriseNetworkAnalyzer(EnterpriseNetworkAnalyzer):
    def __init__(self, config_file: str = "enterprise_config.ini"):
        super().__init__(config_file)
        self.advanced_threat_analyzer = AdvancedThreatAnalyzer(self.config)
        self.quarantine_system = QuarantineSystem(self.config)
        self.stix_generator = STIXReportGenerator()
        self.performance_stats = {
            'analysis_start_time': None,
            'analysis_end_time': None,
            'packets_per_second': 0,
            'memory_usage': 0
        }
    
    async def analyze_pcapng_advanced(self, file_path: str, top_n: int = 10, 
                                    save_report: bool = False, 
                                    enable_vt: bool = False,
                                    behavioral_analysis: bool = True):
        """Расширенный анализ с дополнительными функциями"""
        
        self.performance_stats['analysis_start_time'] = datetime.now()
        file_hash = self.calculate_file_hash(file_path)
        
        logging.info(f"Starting advanced enterprise analysis of {file_path}")
        
        try:
            cap = pyshark.FileCapture(file_path)
        except Exception as e:
            logging.error(f"Error opening file: {e}")
            return
        
        all_packets = []
        high_severity_threats = []
        
        print(f"Advanced Enterprise Analysis: {file_path}")
        print("Processing packets with advanced threat detection...")
        
        try:
            for i, packet in enumerate(cap):
                if i % 1000 == 0:
                    print(f"Processed packets: {i}")
                
                all_packets.append(packet)
                self.stats['total_packets'] += 1
                
                # Расширенный анализ угроз
                if enable_vt:
                    threats = await self.advanced_threat_analyzer.analyze_packet_threats_advanced(packet)
                else:
                    threats = self.threat_analyzer.analyze_packet_threats(packet)
                
                self.stats['threats_found'].extend(threats)
                high_sev = [t for t in threats if t.get('severity') == 'HIGH']
                high_severity_threats.extend(high_sev)
                
                # Сбор статистики
                if 'IP' in packet:
                    src_ip = packet.ip.src
                    dst_ip = packet.ip.dst
                    
                    if not self.is_local_ip(src_ip):
                        self.stats['ip_addresses'].append(src_ip)
                    if not self.is_local_ip(dst_ip):
                        self.stats['ip_addresses'].append(dst_ip)
                
                if 'DNS' in packet and hasattr(packet.dns, 'qry_name'):
                    self.stats['dns_requests'].append(packet.dns.qry_name.lower())
                
                protocol = self.get_protocol_name(packet)
                self.stats['protocols'].append(protocol)
                
        except Exception as e:
            logging.error(f"Error processing packets: {e}")
        finally:
            cap.close()
        
        # Поведенческий анализ
        if behavioral_analysis and len(all_packets) > 1000:
            self.advanced_threat_analyzer.behavioral_analyzer.establish_baseline(all_packets)
            behavioral_anomalies = self.advanced_threat_analyzer.behavioral_analyzer.detect_anomalies(all_packets)
            self.stats['suspicious_activities'].extend(behavioral_anomalies)
        
        # Обнаружение эксфильтрации данных
        exfiltration_signs = self.advanced_threat_analyzer.detect_data_exfiltration(all_packets)
        self.stats['suspicious_activities'].extend(exfiltration_signs)
        
        # Дополнительный анализ
        port_scanners = self.detect_port_scan(all_packets)
        self.stats['suspicious_activities'].extend(port_scanners)
        
        # Расчет производительности
        self.performance_stats['analysis_end_time'] = datetime.now()
        duration = (self.performance_stats['analysis_end_time'] - 
                   self.performance_stats['analysis_start_time']).total_seconds()
        self.performance_stats['packets_per_second'] = self.stats['total_packets'] / duration if duration > 0 else 0
        
        # Генерация отчетов
        self.generate_advanced_report(file_path, file_hash, top_n, save_report)
        
        # Оповещения
        if high_severity_threats:
            self.send_alerts(high_severity_threats, file_path)
        
        # Интеграция с SIEM
        asyncio.run(self.send_to_siem(file_path, self.stats))
        
        logging.info(f"Advanced enterprise analysis completed for {file_path}")
    
    def generate_advanced_report(self, file_path: str, file_hash: str, 
                               top_n: int, save_report: bool):
        """Генерация расширенного отчета безопасности"""
        
        print("\n" + "="*80)
        print("ADVANCED ENTERPRISE SECURITY ANALYSIS REPORT")
        print("="*80)
        
        # Базовая статистика
        ip_counter = Counter(self.stats['ip_addresses'])
        dns_counter = Counter(self.stats['dns_requests'])
        protocol_counter = Counter(self.stats['protocols'])
        
        # Угрозы по категориям
        threat_by_type = Counter([t['type'] for t in self.stats['threats_found']])
        
        print(f"\nSECURITY THREATS SUMMARY:")
        print(f"  Total threats detected: {len(self.stats['threats_found'])}")
        for threat_type, count in threat_by_type.most_common():
            print(f"  {threat_type}: {count}")
        
        print(f"\nSUSPICIOUS ACTIVITIES:")
        for activity in self.stats['suspicious_activities']:
            severity = activity.get('severity', 'UNKNOWN')
            print(f"  [{severity}] {activity['type']}: {activity.get('description', '')}")
        
        # Производительность
        print(f"\nPERFORMANCE STATISTICS:")
        print(f"  Total processing time: {(self.performance_stats['analysis_end_time'] - self.performance_stats['analysis_start_time']).total_seconds():.2f}s")
        print(f"  Packets per second: {self.performance_stats['packets_per_second']:.2f}")
        print(f"  Memory usage: {self.performance_stats.get('memory_usage', 'N/A')} MB")
        
        # Сохранение в базу данных
        if save_report:
            self.save_to_database(file_path, file_hash)
            
            # Расширенный JSON отчет
            report = self.create_comprehensive_report(file_path, file_hash)
            report_file = f"{file_path}_advanced_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # STIX отчет
            stix_report = self.stix_generator.generate_stix_bundle(
                self.stats['threats_found'], 
                {'filename': file_path, 'file_hash': file_hash}
            )
            stix_file = f"{file_path}_stix_report.json"
            with open(stix_file, 'w', encoding='utf-8') as f:
                json.dump(stix_report, f, indent=2, ensure_ascii=False)
            
            print(f"\nReports saved:")
            print(f"  Full report: {report_file}")
            print(f"  STIX report: {stix_file}")

# Утилиты для работы с большими файлами
class LargeFileProcessor:
    @staticmethod
    def split_large_pcap(file_path: str, chunk_size: int = 1000000) -> List[str]:
        """Разделение больших PCAP файлов на части"""
        try:
            import pcap_splitter
            from pcap_splitter.splitter import PcapSplitter
            
            splitter = PcapSplitter(file_path)
            output_files = splitter.split_by_packet_count(chunk_size)
            return output_files
            
        except ImportError:
            logging.warning("pcap-splitter not installed, using fallback method")
            return LargeFileProcessor._fallback_split(file_path, chunk_size)
    
    @staticmethod
    def _fallback_split(file_path: str, chunk_size: int) -> List[str]:
        """Резервный метод разделения файлов"""
        # Простая реализация через tshark
        output_files = []
        base_name = os.path.splitext(file_path)[0]
        
        try:
            # Получение общего количества пакетов
            result = subprocess.run(
                ['capinfos', '-c', file_path], 
                capture_output=True, 
                text=True
            )
            total_packets = int(result.stdout.split(':')[-1].strip())
            
            # Разделение на части
            for i in range(0, total_packets, chunk_size):
                output_file = f"{base_name}_part{i//chunk_size}.pcap"
                subprocess.run([
                    'tshark', '-r', file_path, 
                    '-w', output_file,
                    '-c', str(chunk_size)
                ])
                output_files.append(output_file)
                
        except Exception as e:
            logging.error(f"Fallback split failed: {e}")
        
        return output_files

# Главная функция с расширенными опциями
def main():
    parser = argparse.ArgumentParser(description='Advanced Enterprise Network Analyzer')
    parser.add_argument('file', help='Path to PCAPNG file')
    parser.add_argument('-n', '--top-n', type=int, default=10,
                       help='Number of top results to display (default: 10)')
    parser.add_argument('-s', '--save-report', action='store_true',
                       help='Save detailed report to JSON and database')
    parser.add_argument('-c', '--config', default='enterprise_config.ini',
                       help='Path to configuration file')
    parser.add_argument('--parallel', action='store_true',
                       help='Use parallel processing for large files')
    parser.add_argument('--virustotal', action='store_true',
                       help='Enable VirusTotal integration')
    parser.add_argument('--behavioral', action='store_true',
                       help='Enable behavioral analysis')
    parser.add_argument('--stix', action='store_true',
                       help='Generate STIX report')
    parser.add_argument('--split-size', type=int, default=1000000,
                       help='Packet count per split for large files')
    
    args = parser.parse_args()
    
    # Проверка существования файла
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found")
        sys.exit(1)
    
    # Обработка больших файлов
    file_size = os.path.getsize(args.file) / (1024 * 1024)  # Размер в MB
    if file_size > 500 and not args.parallel:  # Файлы больше 500MB
        print(f"Large file detected ({file_size:.2f} MB). Consider using --parallel option")
    
    # Инициализация расширенного анализатора
    analyzer = AdvancedEnterpriseNetworkAnalyzer(args.config)
    
    if args.parallel:
        parallel_analyzer = ParallelNetworkAnalyzer(analyzer)
        parallel_analyzer.analyze_large_file(args.file, args.split_size)
    else:
        asyncio.run(analyzer.analyze_pcapng_advanced(
            args.file, 
            args.top_n, 
            args.save_report,
            enable_vt=args.virustotal,
            behavioral_analysis=args.behavioral
        ))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("Advanced Enterprise Network Analyzer v2.0")
        print("=" * 50)
        print("Features:")
        print("  • Advanced threat detection")
        print("  • VirusTotal integration")
        print("  • Behavioral analysis")
        print("  • Data exfiltration detection")
        print("  • STIX/TAXII reporting")
        print("  • Large file processing")
        print("  • Performance monitoring")
        print("\nUsage: ./advanced_net_analyzer.py <pcapng_file> [options]")
        print("For more options: ./advanced_net_analyzer.py -h")
