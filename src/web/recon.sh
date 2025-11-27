#!/usr/bin/bash

# Universal reconnaissance script - replaces all previous versions
# Version: 3.0
# Author: kyle

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RATE_LIMIT=10
TIMEOUT=30
THREADS=50

show_help() {
    echo -e "${GREEN}Universal reconnaissance script${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [OPTIONS]"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  -u, --url URL        Target domain (e.g.: example.com)"
    echo "  -f, --file FILE      File with domains (one per line)"
    echo "  -o, --output DIR     Output directory (default: scan_results)"
    echo "  -r, --rate RATE      Rate limit for tools (default: $RATE_LIMIT)"
    echo "  -t, --threads THR    Number of threads (default: $THREADS)"
    echo "  -q, --quiet          Quiet mode (minimal output)"
    echo "  -h, --help           Show this help"
    echo ""
    echo -e "${YELLOW}Operation modes:${NC}"
    echo "  --fast               Fast reconnaissance (only subfinder + httpx)"
    echo "  --full               Full reconnaissance (all tools)"
    echo "  --passive            Passive reconnaissance (no active scanning)"
    echo "  --bughunt            Bug hunting mode (katana + gau + skanuvaty)"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 -u example.com --full"
    echo "  $0 -f domains.txt --fast -o my_scan"
    echo "  $0 -f targets.txt --passive -r 5"
    echo "  $0 -u example.com --bughunt"
    echo "  $0 -u example.com -q" 
    echo ""
    echo -e "${RED}Note: Make sure all tools are installed!${NC}"
}

# Logging
log() {
    if [[ "$QUIET" != "true" ]]; then
        echo -e "${GREEN}[+]${NC} $1"
    fi
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[-]${NC} $1"
}

# Dependency check
check_dependencies() {
    local tools=("subfinder" "httpx" "katana" "nuclei" "waybackurls" "gau" "skanuvaty")
    local missing=()
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing+=("$tool")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing tools: ${missing[*]}"
        echo "Install them with:"
        echo "  go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
        echo "  go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest"
        echo "  go install -v github.com/projectdiscovery/katana/cmd/katana@latest"
        echo "  go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest"
        echo "  go install -v github.com/tomnomnom/waybackurls@latest"
        echo "  go install -v github.com/lc/gau/v2/cmd/gau@latest"
        echo "  go install -v github.com/Edu4rdSHL/skanuvaty@latest"
        exit 1
    fi
}

# Bug hunting scan
bughunt_scan() {
    local domain="$1"
    local output_dir="$2"
    
    log "Starting Bug Hunting scan for: $domain"
    
    cd "$output_dir" || exit 1
    
    # Create directory for domain
    local domain_dir="${domain//\//_}"
    mkdir -p "$domain_dir"
    cd "$domain_dir" || exit 1
    
    log "Running Katana (deep scan)..."
    katana -u "https://$domain" -jc -d 5 -silent -rl "$RATE_LIMIT" > "katana_deep.txt" 2>/dev/null &
    
    log "Running GAU (archive URL collection)..."
    gau "$domain" --subs > "gau_urls.txt" 2>/dev/null &
    
    log "Running Skanuvaty (vulnerability scan)..."
    skanuvaty -d "$domain" -o "skanuvaty_results.txt" 2>/dev/null &
    
    # Wait for all background processes to finish
    wait
    
    # Combine results
    cat "katana_deep.txt" "gau_urls.txt" 2>/dev/null | sort -u > "all_bughunt_urls.txt"
    
    # Check live URLs
    if [[ -s "all_bughunt_urls.txt" ]]; then
        log "Checking live URLs..."
        httpx -l "all_bughunt_urls.txt" -silent -rl "$RATE_LIMIT" -threads "$THREADS" > "bughunt_alive.txt" 2>/dev/null
    fi
    
    # Statistics
    local total_urls=$(wc -l < "all_bughunt_urls.txt" 2>/dev/null || echo 0)
    local alive_urls=$(wc -l < "bughunt_alive.txt" 2>/dev/null || echo 0)
    local skanuvaty_findings=$(wc -l < "skanuvaty_results.txt" 2>/dev/null || echo 0)
    
    log "Bug Hunting results for $domain:"
    log "  Total URLs: $total_urls"
    log "  Live URLs: $alive_urls"
    log "  Skanuvaty findings: $skanuvaty_findings"
    
    cd - > /dev/null || exit 1
}

# Process single domain
process_single_domain() {
    local domain="$1"
    local output_dir="$2"
    
    log "Processing domain: $domain"
    
    cd "$output_dir" || exit 1
    
    # Create directory for domain
    local domain_dir="${domain//\//_}"
    mkdir -p "$domain_dir"
    cd "$domain_dir" || exit 1
    
    # Run tools
    if [[ "$MODE" == "fast" || "$MODE" == "full" ]]; then
        log "Running Subfinder..."
        subfinder -d "$domain" -silent -rl "$RATE_LIMIT" > "subfinder.txt" 2>/dev/null &
    fi
    
    if [[ "$MODE" == "full" ]]; then
        log "Running Katana..."
        katana -u "https://$domain" -silent -rl "$RATE_LIMIT" > "katana.txt" 2>/dev/null &
        
        log "Running Waybackurls..."
        echo "$domain" | waybackurls > "wayback.txt" 2>/dev/null &
        
        log "Running GAU..."
        gau "$domain" --subs > "gau.txt" 2>/dev/null &
    fi
    
    # Wait for all background processes to finish
    wait
    
    # Combine results
    if [[ "$MODE" == "fast" ]]; then
        cat "subfinder.txt" > "all_subdomains.txt" 2>/dev/null
    elif [[ "$MODE" == "full" ]]; then
        cat "subfinder.txt" "katana.txt" 2>/dev/null | sort -u > "all_subdomains.txt"
        cat "wayback.txt" "gau.txt" 2>/dev/null | sort -u > "all_archive_urls.txt"
    fi
    
    # Check live hosts
    if [[ -s "all_subdomains.txt" ]]; then
        log "Checking live subdomains..."
        httpx -l "all_subdomains.txt" -silent -rl "$RATE_LIMIT" -threads "$THREADS" > "alive.txt" 2>/dev/null
    fi
    
    # For archive URLs
    if [[ "$MODE" == "full" && -s "all_archive_urls.txt" ]]; then
        log "Checking Archive URLs..."
        httpx -l "all_archive_urls.txt" -silent -rl "$RATE_LIMIT" -threads "$THREADS" > "archive_alive.txt" 2>/dev/null
    fi
    
    # Nuclei scan (only for full mode)
    if [[ "$MODE" == "full" && -s "alive.txt" ]]; then
        log "Running Nuclei..."
        nuclei -l "alive.txt" -silent -rl "$RATE_LIMIT" -c "$THREADS" > "nuclei_results.txt" 2>/dev/null &
    fi
    
    wait
    
    # Statistics
    local sub_count=$(wc -l < "all_subdomains.txt" 2>/dev/null || echo 0)
    local alive_count=$(wc -l < "alive.txt" 2>/dev/null || echo 0)
    local archive_count=$(wc -l < "archive_alive.txt" 2>/dev/null || echo 0)
    
    log "Results for $domain:"
    log "  Subdomains: $sub_count"
    log "  Live: $alive_count"
    if [[ "$MODE" == "full" ]]; then
        log "  Archive URLs: $archive_count"
    fi
    
    cd - > /dev/null || exit 1
}

# Process file with domains
process_file() {
    local file="$1"
    local output_dir="$2"
    
    if [[ ! -f "$file" ]]; then
        error "File $file does not exist"
        exit 1
    fi
    
    local total_domains=$(wc -l < "$file")
    log "Processing file: $file"
    log "Domains found: $total_domains"
    
    # Create common files
    cd "$output_dir" || exit 1
    > all_subdomains.txt
    > all_alive.txt
    > all_archive_alive.txt
    
    local count=0
    while IFS= read -r domain || [[ -n "$domain" ]]; do
        [[ -z "$domain" ]] && continue
        
        if [[ "$MODE" == "bughunt" ]]; then
            bughunt_scan "$domain" "$output_dir"
        else
            process_single_domain "$domain" "$output_dir"
        fi
        
        ((count++))
        
        # Update common files
        local domain_dir="${domain//\//_}"
        if [[ -f "$domain_dir/all_subdomains.txt" ]]; then
            cat "$domain_dir/all_subdomains.txt" >> "all_subdomains.txt"
        fi
        if [[ -f "$domain_dir/alive.txt" ]]; then
            cat "$domain_dir/alive.txt" >> "all_alive.txt"
        fi
        if [[ -f "$domain_dir/archive_alive.txt" ]]; then
            cat "$domain_dir/archive_alive.txt" >> "all_archive_alive.txt"
        fi
        
    done < "$file"
    
    # Deduplicate common files
    sort -u "all_subdomains.txt" -o "all_subdomains.txt"
    sort -u "all_alive.txt" -o "all_alive.txt"
    sort -u "all_archive_alive.txt" -o "all_archive_alive.txt"
    
    log "Overall results:"
    log "  Total subdomains: $(wc -l < all_subdomains.txt)"
    log "  Total live: $(wc -l < all_alive.txt)"
    if [[ "$MODE" == "full" ]]; then
        log "  Total Archive URLs: $(wc -l < all_archive_alive.txt)"
    fi
    
    cd - > /dev/null || exit 1
}

# Main function
main() {
    # Parse arguments
    URL=""
    FILE=""
    OUTPUT_DIR="scan_results"
    MODE="full"
    QUIET="false"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -u|--url)
                URL="$2"
                shift 2
                ;;
            -f|--file)
                FILE="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -r|--rate)
                RATE_LIMIT="$2"
                shift 2
                ;;
            -t|--threads)
                THREADS="$2"
                shift 2
                ;;
            -q|--quiet)
                QUIET="true"
                shift
                ;;
            --fast)
                MODE="fast"
                shift
                ;;
            --full)
                MODE="full"
                shift
                ;;
            --passive)
                MODE="passive"
                shift
                ;;
            --bughunt)
                MODE="bughunt"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error "Unknown argument: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Validate input
    if [[ -z "$URL" && -z "$FILE" ]]; then
        error "No domain or file specified"
        show_help
        exit 1
    fi
    
    if [[ -n "$URL" && -n "$FILE" ]]; then
        error "Both domain and file specified. Use only one."
        show_help
        exit 1
    fi
    
    # Check dependencies
    check_dependencies
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    log "Results will be saved to: $OUTPUT_DIR"
    
    # Start execution
    local start_time=$(date +%s)
    
    if [[ -n "$URL" ]]; then
        log "Starting $MODE mode for domain: $URL"
        if [[ "$MODE" == "bughunt" ]]; then
            bughunt_scan "$URL" "$OUTPUT_DIR"
        else
            process_single_domain "$URL" "$OUTPUT_DIR"
        fi
    else
        log "Starting $MODE mode for file: $FILE"
        process_file "$FILE" "$OUTPUT_DIR"
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "Scan completed in $duration seconds"
    log "All results in: $OUTPUT_DIR"
    
    # Show summary
    if [[ -n "$URL" ]]; then
        local domain_dir="${URL//\//_}"
        echo ""
        echo -e "${GREEN}📊 SUMMARY for $URL:${NC}"
        echo -e "  📁 Directory: $OUTPUT_DIR/$domain_dir"
        
        if [[ "$MODE" == "bughunt" ]]; then
            if [[ -f "$OUTPUT_DIR/$domain_dir/bughunt_alive.txt" ]]; then
                echo -e "  🎯 Bug Hunt URLs: $(wc -l < "$OUTPUT_DIR/$domain_dir/bughunt_alive.txt")"
            fi
            if [[ -f "$OUTPUT_DIR/$domain_dir/skanuvaty_results.txt" ]]; then
                echo -e "  🔍 Skanuvaty findings: $(wc -l < "$OUTPUT_DIR/$domain_dir/skanuvaty_results.txt")"
            fi
        else
            if [[ -f "$OUTPUT_DIR/$domain_dir/alive.txt" ]]; then
                echo -e "  🟢 Live hosts: $(wc -l < "$OUTPUT_DIR/$domain_dir/alive.txt")"
            fi
            if [[ -f "$OUTPUT_DIR/$domain_dir/archive_alive.txt" ]]; then
                echo -e "  🔄 Archive URLs: $(wc -l < "$OUTPUT_DIR/$domain_dir/archive_alive.txt")"
            fi
        fi
    else
        echo ""
        echo -e "${GREEN}📊 OVERALL SUMMARY:${NC}"
        echo -e "  📁 Directory: $OUTPUT_DIR"
        if [[ -f "$OUTPUT_DIR/all_alive.txt" ]]; then
            echo -e "  🟢 Total live hosts: $(wc -l < "$OUTPUT_DIR/all_alive.txt")"
        fi
        if [[ "$MODE" == "bughunt" && -f "$OUTPUT_DIR/all_bughunt_urls.txt" ]]; then
            echo -e "  🎯 Total Bug Hunt URLs: $(wc -l < "$OUTPUT_DIR/all_bughunt_urls.txt")"
        fi
    fi
}

# Run main function
main "$@"
