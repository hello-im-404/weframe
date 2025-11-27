#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
ORANGE='\033[0;33m'
NC='\033[0m'

# Configuration
BASE_DIR="/home/$USER/OSINT"
CONFIG_FILE="$BASE_DIR/.osint_config"
CURRENT_CASE_FILE="/tmp/current_case.txt"

mkdir -p "$BASE_DIR"

create_case() {
    echo -e "${BLUE}Creating new case${NC}"
    read -p "Case name: " CASE_NAME
    
    if [[ -z "$CASE_NAME" ]]; then
        echo -e "${RED}Case name cannot be empty!${NC}"
        return 1
    fi
    
    WORK_DIR="$BASE_DIR/$CASE_NAME"
    
    if [[ -d "$WORK_DIR" ]]; then
        echo -e "${YELLOW}Case '$CASE_NAME' already exists!${NC}"
        read -p "Overwrite? (y/N): " OVERWRITE
        if [[ ! $OVERWRITE =~ ^[Yy]$ ]]; then
            return 1
        fi
        rm -rf "$WORK_DIR"
    fi
    
    mkdir -p "$WORK_DIR"/{videos,photos,full_info,tools,documents,logs,export,connections,screenshots}
    
    mkdir -p "$WORK_DIR/full_info"
    cat > "$WORK_DIR/full_info/categories.txt" << EOF
Full name:
Nickname:
Phone numbers:
Social Media:
Car numbers:
Addresses:
Email:
Work/Education:
Birth date:
Passport details:
Other:
EOF

    mkdir -p "$WORK_DIR/connections/relatives"
    mkdir -p "$WORK_DIR/connections/friends"
    mkdir -p "$WORK_DIR/connections/colleagues"
    
    cat > "$WORK_DIR/README.md" << EOF
# Case: $CASE_NAME

## Main Target:
- Full name: 
- Nickname:
- Phone numbers: 
- Addresses: 

## Connections 
### Relatives
- 

### Friends 
- 

### Colleagues
- 

## Chronology of events
- Date: Event 

## Conclusions 
...

### Next Steps
1. 
2. 
3. 
EOF

    echo "$(date): Case '$CASE_NAME' created" >> "$WORK_DIR/logs/activity.log"
    
    echo "$WORK_DIR" > "$CURRENT_CASE_FILE"
    echo -e "${GREEN}Case '$CASE_NAME' created in $WORK_DIR${NC}"
    echo -e "${CYAN}Structure:${NC}"
    tree "$WORK_DIR" -L 2
}

add_main_data() {
    if [[ ! -f "$CURRENT_CASE_FILE" ]]; then
        echo -e "${RED}First, create or select a case!${NC}"
        return 1
    fi
    
    WORK_DIR=$(cat "$CURRENT_CASE_FILE")
    
    echo -e "${YELLOW}Adding data for main target${NC}"
    echo "1  - Full name"
    echo "2  - Nickname"
    echo "3  - Phone number"
    echo "4  - Social media"
    echo "5  - Car"
    echo "6  - Address"
    echo "7  - Email"
    echo "8  - Work/Education"
    echo "9  - Birth date"
    echo "10 - Passport details"
    echo "11 - Other"
    read -p "Select data type: " choice
    
    case $choice in
        1) read -p "Enter full name: " data
           echo "Full name: $data" >> "$WORK_DIR/full_info/categories.txt"
           ;;
        2) read -p "Enter nickname: " data
           echo "Nickname: $data" >> "$WORK_DIR/full_info/categories.txt"
           ;;
        3) read -p "Enter phone number: " data
           echo "Phone numbers: $data" >> "$WORK_DIR/full_info/categories.txt"
           ;;
        4) read -p "Enter social media: " data
           echo "Social Media: $data" >> "$WORK_DIR/full_info/categories.txt"
           ;;
        5) read -p "Enter car number: " data
           echo "Car numbers: $data" >> "$WORK_DIR/full_info/categories.txt"
           ;;
        6) read -p "Enter address: " data
           echo "Addresses: $data" >> "$WORK_DIR/full_info/categories.txt"
           ;;
        7) read -p "Enter email: " data
           echo "Email: $data" >> "$WORK_DIR/full_info/categories.txt"
           ;;
        8) read -p "Enter work/education information: " data
           echo "Work/Education: $data" >> "$WORK_DIR/full_info/categories.txt"
           ;;
        9) read -p "Enter birth date: " data
           echo "Birth date: $data" >> "$WORK_DIR/full_info/categories.txt"
           ;;
        10) read -p "Enter passport details: " data
           echo "Passport details: $data" >> "$WORK_DIR/full_info/categories.txt"
           ;;
        11) read -p "Enter other information: " data
           echo "Other: $data" >> "$WORK_DIR/full_info/categories.txt"
           ;;
        *) echo -e "${RED}Invalid choice${NC}" ; return 1 ;;
    esac
    
    echo "$(date): Added main target data type $choice: $data" >> "$WORK_DIR/logs/activity.log"
    echo -e "${GREEN}Data added!${NC}"
}

add_relative() {
    if [[ ! -f "$CURRENT_CASE_FILE" ]]; then
        echo -e "${RED}First, create or select a case!${NC}"
        return 1
    fi
    
    WORK_DIR=$(cat "$CURRENT_CASE_FILE")
    
    echo -e "${PURPLE}Adding relative${NC}"
    echo "1  - Mother"
    echo "2  - Father" 
    echo "3  - Brother"
    echo "4  - Sister"
    echo "5  - Husband"
    echo "6  - Wife"
    echo "7  - Grandfather"
    echo "8  - Grandmother"
    echo "9  - Son"
    echo "10 - Daughter"
    echo "11 - Other relative"
    read -p "Select relationship type: " relation_type
    
    case $relation_type in
        1) relation="Mother" ;;
        2) relation="Father" ;;
        3) relation="Brother" ;;
        4) relation="Sister" ;;
        5) relation="Husband" ;;
        6) relation="Wife" ;;
        7) relation="Grandfather" ;;
        8) relation="Grandmother" ;;
        9) relation="Son" ;;
        10) relation="Daughter" ;;
        11) read -p "Enter relationship type: " relation ;;
        *) echo -e "${RED}Invalid choice${NC}" ; return 1 ;;
    esac
    
    read -p "Enter relative's full name: " name
    read -p "Enter age: " age
    read -p "Enter phone number: " phone
    read -p "Enter address: " address
    read -p "Enter nickname (if any): " nickname
    read -p "Enter additional information: " info
    
    # Create file for relative
    RELATIVE_FILE="$WORK_DIR/connections/relatives/${relation}_${name// /_}.txt"
    cat > "$RELATIVE_FILE" << EOF
Relationship type: $relation
Full name: $name
Nickname: $nickname
Age: $age
Phone: $phone
Address: $address
Additional: $info
Date added: $(date)
EOF

    echo "$(date): Added relative: $relation - $name" >> "$WORK_DIR/logs/activity.log"
    echo -e "${GREEN}Relative '$name' added as '$relation'!${NC}"
}

add_friend() {
    if [[ ! -f "$CURRENT_CASE_FILE" ]]; then
        echo -e "${RED}First, create or select a case!${NC}"
        return 1
    fi
    
    WORK_DIR=$(cat "$CURRENT_CASE_FILE")
    
    echo -e "${CYAN}Adding friend${NC}"
    echo "1 - Girl"
    echo "2 - Boy"
    read -p "Select gender: " gender_choice
    
    case $gender_choice in
        1) gender="Girl" ;;
        2) gender="Boy" ;;
        *) echo -e "${RED}Invalid choice${NC}" ; return 1 ;;
    esac
    
    read -p "Enter friend's name: " name
    read -p "Enter nickname: " nickname
    read -p "Enter age: " age
    read -p "Enter phone number: " phone
    read -p "How they met: " met_how
    read -p "Common interests: " interests
    read -p "Enter additional information: " info
    
    # Create file for friend
    FRIEND_FILE="$WORK_DIR/connections/friends/${gender}_${name// /_}.txt"
    cat > "$FRIEND_FILE" << EOF
Gender: $gender
Name: $name
Nickname: $nickname
Age: $age
Phone: $phone
How met: $met_how
Interests: $interests
Additional: $info
Date added: $(date)
EOF

    echo "$(date): Added friend: $gender - $name" >> "$WORK_DIR/logs/activity.log"
    echo -e "${GREEN}Friend '$name' added!${NC}"
}

add_colleague() {
    if [[ ! -f "$CURRENT_CASE_FILE" ]]; then
        echo -e "${RED}First, create or select a case!${NC}"
        return 1
    fi
    
    WORK_DIR=$(cat "$CURRENT_CASE_FILE")
    
    echo -e "${ORANGE}Adding colleague${NC}"
    read -p "Enter colleague's full name: " name
    read -p "Enter position: " position
    read -p "Enter workplace: " workplace
    read -p "Enter phone number: " phone
    read -p "Enter email: " email
    read -p "Period of joint work: " period
    read -p "Enter additional information: " info
    
    # Create file for colleague
    COLLEAGUE_FILE="$WORK_DIR/connections/colleagues/${name// /_}.txt"
    cat > "$COLLEAGUE_FILE" << EOF
Full name: $name
Position: $position
Workplace: $workplace
Phone: $phone
Email: $email
Work period: $period
Additional: $info
Date added: $(date)
EOF

    echo "$(date): Added colleague: $name" >> "$WORK_DIR/logs/activity.log"
    echo -e "${GREEN}Colleague '$name' added!${NC}"
}

manage_connections() {
    if [[ ! -f "$CURRENT_CASE_FILE" ]]; then
        echo -e "${RED}First, create or select a case!${NC}"
        return 1
    fi
    
    WORK_DIR=$(cat "$CURRENT_CASE_FILE")
    
    while true; do
        echo -e "\n${PURPLE}=== Connection Management ===${NC}"
        echo "1 - Add relative"
        echo "2 - Add friend"
        echo "3 - Add colleague"
        echo "4 - Show all relatives"
        echo "5 - Show all friends"
        echo "6 - Show all colleagues"
        echo "7 - Back"
        read -p "Select action: " conn_choice
        
        case $conn_choice in
            1) add_relative ;;
            2) add_friend ;;
            3) add_colleague ;;
            4) show_relatives ;;
            5) show_friends ;;
            6) show_colleagues ;;
            7) break ;;
            *) echo -e "${RED}Invalid choice${NC}" ;;
        esac
    done
}

show_relatives() {
    if [[ ! -f "$CURRENT_CASE_FILE" ]]; then
        echo -e "${RED}First, create or select a case!${NC}"
        return 1
    fi
    
    WORK_DIR=$(cat "$CURRENT_CASE_FILE")
    RELATIVES_DIR="$WORK_DIR/connections/relatives"
    
    echo -e "\n${PURPLE}=== Relatives ===${NC}"
    if [[ -z "$(ls -A "$RELATIVES_DIR")" ]]; then
        echo -e "${YELLOW}No relatives added${NC}"
        return
    fi
    
    for file in "$RELATIVES_DIR"/*.txt; do
        if [[ -f "$file" ]]; then
            echo -e "${GREEN}$(basename "$file" .txt):${NC}"
            cat "$file"
            echo "---"
        fi
    done
}

show_friends() {
    if [[ ! -f "$CURRENT_CASE_FILE" ]]; then
        echo -e "${RED}First, create or select a case!${NC}"
        return 1
    fi
    
    WORK_DIR=$(cat "$CURRENT_CASE_FILE")
    FRIENDS_DIR="$WORK_DIR/connections/friends"
    
    echo -e "\n${CYAN}=== Friends ===${NC}"
    if [[ -z "$(ls -A "$FRIENDS_DIR")" ]]; then
        echo -e "${YELLOW}No friends added${NC}"
        return
    fi
    
    for file in "$FRIENDS_DIR"/*.txt; do
        if [[ -f "$file" ]]; then
            echo -e "${GREEN}$(basename "$file" .txt):${NC}"
            cat "$file"
            echo "---"
        fi
    done
}

show_colleagues() {
    if [[ ! -f "$CURRENT_CASE_FILE" ]]; then
        echo -e "${RED}First, create or select a case!${NC}"
        return 1
    fi
    
    WORK_DIR=$(cat "$CURRENT_CASE_FILE")
    COLLEAGUES_DIR="$WORK_DIR/connections/colleagues"
    
    echo -e "\n${ORANGE}=== Colleagues ===${NC}"
    if [[ -z "$(ls -A "$COLLEAGUES_DIR")" ]]; then
        echo -e "${YELLOW}No colleagues added${NC}"
        return
    fi
    
    for file in "$COLLEAGUES_DIR"/*.txt; do
        if [[ -f "$file" ]]; then
            echo -e "${GREEN}$(basename "$file" .txt):${NC}"
            cat "$file"
            echo "---"
        fi
    done
}

show_case_data() {
    if [[ ! -f "$CURRENT_CASE_FILE" ]]; then
        echo -e "${RED}First, create or select a case!${NC}"
        return 1
    fi
    
    WORK_DIR=$(cat "$CURRENT_CASE_FILE")
    echo -e "${YELLOW}=== Main Target Data ===${NC}"
    cat "$WORK_DIR/full_info/categories.txt"
    echo
    show_relatives
    echo
    show_friends
    echo
    show_colleagues
}

generate_report() {
    if [[ ! -f "$CURRENT_CASE_FILE" ]] || [[ ! -d $(cat "$CURRENT_CASE_FILE") ]]; then
        echo -e "${RED}First, create or select a case!${NC}"
        return 1
    fi
    
    WORK_DIR=$(cat "$CURRENT_CASE_FILE")
    REPORT_FILE="$WORK_DIR/export/report_$(date +%Y%m%d_%H%M%S).html"
    
    # Read main target data
    local full_name=$(grep "Full name:" "$WORK_DIR/full_info/categories.txt" | cut -d: -f2- | sed 's/^ *//')
    local nickname=$(grep "Nickname:" "$WORK_DIR/full_info/categories.txt" | cut -d: -f2- | sed 's/^ *//')
    local phones=$(grep "Phone numbers:" "$WORK_DIR/full_info/categories.txt" | cut -d: -f2- | sed 's/^ *//')
    local social=$(grep "Social Media:" "$WORK_DIR/full_info/categories.txt" | cut -d: -f2- | sed 's/^ *//')
    local cars=$(grep "Car numbers:" "$WORK_DIR/full_info/categories.txt" | cut -d: -f2- | sed 's/^ *//')
    local addresses=$(grep "Addresses:" "$WORK_DIR/full_info/categories.txt" | cut -d: -f2- | sed 's/^ *//')
    local emails=$(grep "Email:" "$WORK_DIR/full_info/categories.txt" | cut -d: -f2- | sed 's/^ *//')
    local work=$(grep "Work/Education:" "$WORK_DIR/full_info/categories.txt" | cut -d: -f2- | sed 's/^ *//')
    local birth=$(grep "Birth date:" "$WORK_DIR/full_info/categories.txt" | cut -d: -f2- | sed 's/^ *//')
    local passport=$(grep "Passport details:" "$WORK_DIR/full_info/categories.txt" | cut -d: -f2- | sed 's/^ *//')
    local other=$(grep "Other:" "$WORK_DIR/full_info/categories.txt" | cut -d: -f2- | sed 's/^ *//')
    
    # Generate HTML for relatives
    local relatives_html=""
    for file in "$WORK_DIR/connections/relatives"/*.txt; do
        if [[ -f "$file" ]]; then
            local rel_name=$(grep "Full name:" "$file" | cut -d: -f2- | sed 's/^ *//')
            local rel_type=$(grep "Relationship type:" "$file" | cut -d: -f2- | sed 's/^ *//')
            local rel_nick=$(grep "Nickname:" "$file" | cut -d: -f2- | sed 's/^ *//')
            local rel_phone=$(grep "Phone:" "$file" | cut -d: -f2- | sed 's/^ *//')
            local rel_address=$(grep "Address:" "$file" | cut -d: -f2- | sed 's/^ *//')
            relatives_html+="<div class='connection-card'><div class='connection-header'><h3>$rel_type</h3></div><div class='connection-body'><p><strong>Full name:</strong> $rel_name</p><p><strong>Nickname:</strong> $rel_nick</p><p><strong>Phone:</strong> $rel_phone</p><p><strong>Address:</strong> $rel_address</p></div></div>"
        fi
    done
    
    # Generate HTML for friends
    local friends_html=""
    for file in "$WORK_DIR/connections/friends"/*.txt; do
        if [[ -f "$file" ]]; then
            local friend_name=$(grep "Name:" "$file" | cut -d: -f2- | sed 's/^ *//')
            local friend_gender=$(grep "Gender:" "$file" | cut -d: -f2- | sed 's/^ *//')
            local friend_nick=$(grep "Nickname:" "$file" | cut -d: -f2- | sed 's/^ *//')
            local friend_phone=$(grep "Phone:" "$file" | cut -d: -f2- | sed 's/^ *//')
            local friend_met=$(grep "How met:" "$file" | cut -d: -f2- | sed 's/^ *//')
            local friend_interests=$(grep "Interests:" "$file" | cut -d: -f2- | sed 's/^ *//')
            friends_html+="<div class='connection-card'><div class='connection-header'><h3>$friend_gender: $friend_name</h3></div><div class='connection-body'><p><strong>Nickname:</strong> $friend_nick</p><p><strong>Phone:</strong> $friend_phone</p><p><strong>How met:</strong> $friend_met</p><p><strong>Interests:</strong> $friend_interests</p></div></div>"
        fi
    done
    
    # Generate HTML for colleagues
    local colleagues_html=""
    for file in "$WORK_DIR/connections/colleagues"/*.txt; do
        if [[ -f "$file" ]]; then
            local col_name=$(grep "Full name:" "$file" | cut -d: -f2- | sed 's/^ *//')
            local col_position=$(grep "Position:" "$file" | cut -d: -f2- | sed 's/^ *//')
            local col_workplace=$(grep "Workplace:" "$file" | cut -d: -f2- | sed 's/^ *//')
            local col_phone=$(grep "Phone:" "$file" | cut -d: -f2- | sed 's/^ *//')
            colleagues_html+="<div class='connection-card'><div class='connection-header'><h3>$col_name</h3></div><div class='connection-body'><p><strong>Position:</strong> $col_position</p><p><strong>Workplace:</strong> $col_workplace</p><p><strong>Phone:</strong> $col_phone</p></div></div>"
        fi
    done
    
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Report - $(basename "$WORK_DIR")</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Roboto:wght@300;400;500;700&display=swap');
        
        :root {
            --primary: #2c3e50;
            --secondary: #34495e;
            --accent: #3498db;
            --accent2: #9b59b6;
            --accent3: #e74c3c;
            --light: #ecf0f1;
            --dark: #1a1a1a;
            --success: #27ae60;
            --warning: #f39c12;
            --danger: #e74c3c;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: var(--dark);
            line-height: 1.6;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header {
            text-align: center;
            padding: 40px 0;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border-radius: 20px;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="M0,0 L100,0 L100,100 Z" fill="rgba(255,255,255,0.1)"/></svg>');
            background-size: cover;
        }
        
        .header h1 {
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.5em;
            margin-bottom: 10px;
            position: relative;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
            position: relative;
        }
        
        .metadata {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 25px 0;
        }
        
        .meta-item {
            background: var(--light);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid var(--accent);
        }
        
        .section-title {
            font-family: 'JetBrains Mono', monospace;
            color: var(--primary);
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid var(--accent);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-title::before {
            content: '▶';
            color: var(--accent);
            font-size: 0.8em;
        }
        
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .data-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e0e0;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .data-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        .data-card h3 {
            color: var(--secondary);
            margin-bottom: 15px;
            font-family: 'JetBrains Mono', monospace;
            border-bottom: 2px solid var(--light);
            padding-bottom: 5px;
        }
        
        .connections-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin: 25px 0;
        }
        
        .connection-card {
            background: linear-gradient(135deg, #fff, #f8f9fa);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
        }
        
        .connection-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
        }
        
        .connection-header {
            background: linear-gradient(135deg, var(--accent2), var(--accent));
            color: white;
            padding: 15px 20px;
        }
        
        .connection-header h3 {
            margin: 0;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1em;
        }
        
        .connection-body {
            padding: 20px;
        }
        
        .connection-body p {
            margin: 8px 0;
            padding: 5px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .connection-body p:last-child {
            border-bottom: none;
        }
        
        .tag {
            display: inline-block;
            background: var(--accent);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            margin: 2px;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: white;
            font-family: 'JetBrains Mono', monospace;
            opacity: 0.8;
        }
        
        .risk-level {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 25px;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .risk-low { background: var(--success); color: white; }
        .risk-medium { background: var(--warning); color: white; }
        .risk-high { background: var(--danger); color: white; }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .data-grid {
                grid-template-columns: 1fr;
            }
            
            .connections-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕵️ OSINT INTELLIGENCE REPORT</h1>
            <div class="subtitle">Case: $(basename "$WORK_DIR")</div>
        </div>
        
        <div class="glass-card">
            <h2 class="section-title">📊 Executive Summary</h2>
            <div class="metadata">
                <div class="meta-item">
                    <strong>🆔 Case ID:</strong><br>$(basename "$WORK_DIR")
                </div>
                <div class="meta-item">
                    <strong>📅 Generated:</strong><br>$(date +"%d.%m.%Y %H:%M:%S")
                </div>
                <div class="meta-item">
                    <strong>👤 Subject:</strong><br>$full_name
                </div>
                <div class="meta-item">
                    <strong>🎯 Nickname:</strong><br>$nickname
                </div>
            </div>
            
            <div class="risk-level risk-medium">
                🔍 INVESTIGATION IN PROGRESS
            </div>
        </div>

        <div class="glass-card">
            <h2 class="section-title">👤 Primary Subject</h2>
            <div class="data-grid">
                <div class="data-card">
                    <h3>🔑 Basic Information</h3>
                    <p><strong>Full Name:</strong> $full_name</p>
                    <p><strong>Nickname:</strong> $nickname</p>
                    <p><strong>Date of Birth:</strong> $birth</p>
                    <p><strong>Passport:</strong> $passport</p>
                </div>
                
                <div class="data-card">
                    <h3>📞 Contact Details</h3>
                    <p><strong>Phones:</strong> $phones</p>
                    <p><strong>Emails:</strong> $emails</p>
                    <p><strong>Addresses:</strong> $addresses</p>
                </div>
                
                <div class="data-card">
                    <h3>🌐 Digital Presence</h3>
                    <p><strong>Social Media:</strong> $social</p>
                    <p><strong>Work/Education:</strong> $work</p>
                </div>
                
                <div class="data-card">
                    <h3>🚗 Assets & Properties</h3>
                    <p><strong>Vehicles:</strong> $cars</p>
                    <p><strong>Additional Info:</strong> $other</p>
                </div>
            </div>
        </div>

        <div class="glass-card">
            <h2 class="section-title">👨‍👩‍👧‍👦 Family Connections</h2>
            <div class="connections-grid">
                $([ -z "$relatives_html" ] && echo "<div class='connection-card'><div class='connection-header'><h3>No Family Data</h3></div><div class='connection-body'><p>No relatives information available</p></div></div>" || echo "$relatives_html")
            </div>
        </div>

        <div class="glass-card">
            <h2 class="section-title">👥 Social Network</h2>
            <div class="connections-grid">
                $([ -z "$friends_html" ] && echo "<div class='connection-card'><div class='connection-header'><h3>No Friends Data</h3></div><div class='connection-body'><p>No friends information available</p></div></div>" || echo "$friends_html")
            </div>
        </div>

        <div class="glass-card">
            <h2 class="section-title">💼 Professional Contacts</h2>
            <div class="connections-grid">
                $([ -z "$colleagues_html" ] && echo "<div class='connection-card'><div class='connection-header'><h3>No Colleagues Data</h3></div><div class='connection-body'><p>No colleagues information available</p></div></div>" || echo "$colleagues_html")
            </div>
        </div>

        <div class="footer">
            <p>🔒 CONFIDENTIAL - FOR AUTHORIZED PERSONNEL ONLY</p>
            <p>Generated by OSINT Case Manager | $(date +"%Y")</p>
        </div>
    </div>
</body>
</html>
EOF
    
    echo -e "${GREEN}🎉 HTML report created: $REPORT_FILE${NC}"
}

list_cases() {
    echo -e "${BLUE}Existing cases:${NC}"
    if [[ ! -d "$BASE_DIR" ]] || [[ -z "$(ls -A "$BASE_DIR")" ]]; then
        echo -e "${YELLOW}No cases found${NC}"
        return 1
    fi
    
    local i=1
    local cases=()
    for dir in "$BASE_DIR"/*; do
        if [[ -d "$dir" ]]; then
            cases[i]="$dir"
            echo -e "${GREEN}$i.${NC} $(basename "$dir")"
            ((i++))
        fi
    done
    
    read -p "Select case to work with (number): " case_num
    if [[ $case_num =~ ^[0-9]+$ ]] && [[ $case_num -ge 1 ]] && [[ $case_num -lt $i ]]; then
        selected_case="${cases[case_num]}"
        echo "$selected_case" > "$CURRENT_CASE_FILE"
        echo -e "${GREEN}Selected case: $(basename "$selected_case")${NC}"
    else
        echo -e "${RED}Invalid choice${NC}"
    fi
}

quick_actions() {
    if [[ ! -f "$CURRENT_CASE_FILE" ]]; then
        echo -e "${RED}First, create or select a case!${NC}"
        return 1
    fi
    
    WORK_DIR=$(cat "$CURRENT_CASE_FILE")
    
    echo -e "${PURPLE}Quick actions for case: $(basename "$WORK_DIR")${NC}"
    echo "1 - Open case directory"
    echo "2 - View README"
    echo "3 - View logs"
    echo "4 - Export all data"
    read -p "Select action: " action
    
    case $action in
        1) xdg-open "$WORK_DIR" 2>/dev/null || echo -e "${YELLOW}Directory: $WORK_DIR${NC}" ;;
        2) cat "$WORK_DIR/README.md" | less ;;
        3) cat "$WORK_DIR/logs/activity.log" | less ;;
        4) tar -czf "$WORK_DIR/export/full_backup_$(date +%Y%m%d).tar.gz" "$WORK_DIR" 2>/dev/null
           echo -e "${GREEN}Backup created in $WORK_DIR/export/${NC}" ;;
        *) echo -e "${RED}Invalid choice${NC}" ;;
    esac
}

show_current_case() {
    if [[ -f "$CURRENT_CASE_FILE" ]] && [[ -d $(cat "$CURRENT_CASE_FILE") ]]; then
        WORK_DIR=$(cat "$CURRENT_CASE_FILE")
        echo -e "${GREEN}Current case: $(basename "$WORK_DIR")${NC}"
        echo -e "${CYAN}Path: $WORK_DIR${NC}"
    else
        echo -e "${YELLOW}No case selected${NC}"
    fi
}

while true; do
    echo -e "\n${BLUE}=== OSINT Case Manager ===${NC}"
    show_current_case
    echo -e "${CYAN}Main actions:${NC}"
    echo "1 - Create new case"
    echo "2 - Select existing case"
    echo "3 - Add main target data"
    echo "4 - Connection management"
    echo "5 - Show all data"
    echo "6 - Generate HTML report"
    echo -e "${PURPLE}Additional:${NC}"
    echo "7 - Quick actions"
    echo "8 - Show all cases"
    echo "9 - Exit"
    read -p "Select action: " main_choice

    case $main_choice in
        1) create_case ;;
        2) list_cases ;;
        3) add_main_data ;;
        4) manage_connections ;;
        5) show_case_data ;;
        6) generate_report ;;
        7) quick_actions ;;
        8) echo -e "${BLUE}All cases:${NC}"; tree "$BASE_DIR" -L 1 -d 2>/dev/null || ls -la "$BASE_DIR" ;;
        9) echo -e "${GREEN}Good luck with your investigation! 🕵️${NC}"; exit 0 ;;
        *) echo -e "${RED}Invalid choice${NC}" ;;
    esac
done
