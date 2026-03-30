#!/bin/bash

# 自动化工作流执行器
# 定义和执行多步骤自动化工作流

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOWS_DIR="$SCRIPT_DIR/../memory/workflows"
LOG_DIR="$SCRIPT_DIR/../memory/workflow-logs"

# 确保目录存在
mkdir -p "$WORKFLOWS_DIR"
mkdir -p "$LOG_DIR"

# 显示用法
show_usage() {
    cat << 'EOF'
自动化工作流执行器

用法:
    workflow.sh <action> [options]

动作:
    list          列出所有工作流
    create        创建新工作流
    run           执行工作流
    show          显示工作流详情
    edit          编辑工作流
    delete        删除工作流
    logs          查看工作流日志

创建选项:
    -n, --name <name>          工作流名称
    -d, --description <desc>   描述
    -s, --steps <steps>        步骤（JSON数组）

执行选项:
    -n, --name <name>          工作流名称
    -v, --variables <vars>      变量（JSON对象）
    -f, --foreground            前台运行

示例:
    workflow.sh list
    workflow.sh create -n "每日检查" -d "执行每日检查任务"
    workflow.sh run "每日检查"
    workflow.sh logs "每日检查"
EOF
}

# 生成工作流文件名
get_workflow_file() {
    local name="$1"
    echo "$WORKFLOWS_DIR/${name}.json"
}

# 生成日志文件名
get_log_file() {
    local name="$1"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    echo "$LOG_DIR/${name}_${timestamp}.log"
}

# 列出所有工作流
list_workflows() {
    echo "📋 工作流列表"
    echo "==========="

    if [ -z "$(ls -A "$WORKFLOWS_DIR" 2>/dev/null)" ]; then
        echo "还没有工作流"
        return
    fi

    for file in "$WORKFLOWS_DIR"/*.json; do
        if [ -f "$file" ]; then
            name=$(jq -r '.name' "$file" 2>/dev/null || echo "Unknown")
            desc=$(jq -r '.description' "$file" 2>/dev/null || echo "No description")
            steps=$(jq -r '.steps | length' "$file" 2>/dev/null || echo 0)
            printf "  %-30s %s (%d 步)\n" "$name" "$desc" "$steps"
        fi
    done
}

# 创建新工作流
create_workflow() {
    local name=""
    local description=""
    local steps="[]"

    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name)
                name="$2"
                shift 2
                ;;
            -d|--description)
                description="$2"
                shift 2
                ;;
            -s|--steps)
                steps="$2"
                shift 2
                ;;
            *)
                echo "未知选项: $1"
                exit 1
                ;;
        esac
    done

    if [ -z "$name" ]; then
        echo "❌ 错误: 工作流名称不能为空"
        exit 1
    fi

    local file=$(get_workflow_file "$name")

    if [ -f "$file" ]; then
        echo "❌ 错误: 工作流已存在"
        exit 1
    fi

    # 创建工作流文件
    cat > "$file" << EOF
{
  "name": "${name}",
  "description": "${description}",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "updated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "enabled": true,
  "variables": {},
  "steps": ${steps}
}
EOF

    echo "✅ 工作流已创建: $name"
}

# 执行工作流
run_workflow() {
    local name="$1"
    local variables="{}"
    local foreground=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name)
                name="$2"
                shift 2
                ;;
            -v|--variables)
                variables="$2"
                shift 2
                ;;
            -f|--foreground)
                foreground=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    local file=$(get_workflow_file "$name")

    if [ ! -f "$file" ]; then
        echo "❌ 错误: 工作流不存在"
        exit 1
    fi

    # 检查工作流是否启用
    local enabled=$(jq -r '.enabled' "$file")
    if [ "$enabled" != "true" ]; then
        echo "⚠️  工作流已禁用"
        exit 0
    fi

    local log_file=$(get_log_file "$name")

    echo "🚀 执行工作流: $name"
    echo "📝 日志文件: $log_file"
    echo ""

    # 加载工作流
    local steps=$(jq -c '.steps' "$file")

    # 执行每个步骤
    local step_num=0
    local success=true

    while IFS= read -r step; do
        ((step_num++))
        local step_name=$(echo "$step" | jq -r '.name // "Step ${step_num}"')
        local step_command=$(echo "$step" | jq -r '.command // empty')
        local step_script=$(echo "$step" | jq -r '.script // empty')

        echo "[$step_num] 执行: $step_name"

        if [ -n "$step_command" ]; then
            if [ "$foreground" = true ]; then
                echo "$step_command" >> "$log_file"
                eval "$step_command" 2>&1 | tee -a "$log_file"
                if [ ${PIPESTATUS[0]} -ne 0 ]; then
                    echo "❌ 步骤执行失败: $step_name"
                    success=false
                    break
                fi
            else
                echo "$step_command" >> "$log_file"
                nohup bash -c "$step_command" >> "$log_file" 2>&1 &
                echo "   后台运行中..."
            fi
        fi

        if [ -n "$step_script" ]; then
            if [ -f "$step_script" ]; then
                if [ "$foreground" = true ]; then
                    bash "$step_script" >> "$log_file" 2>&1
                    if [ $? -ne 0 ]; then
                        echo "❌ 脚本执行失败: $step_script"
                        success=false
                        break
                    fi
                else
                    nohup bash "$step_script" >> "$log_file" 2>&1 &
                    echo "   后台运行中..."
                fi
            else
                echo "⚠️  脚本不存在: $step_script"
            fi
        fi

        # 步骤之间的延迟
        local delay=$(echo "$step" | jq -r '.delay // 0')
        if [ $delay -gt 0 ]; then
            echo "   等待 ${delay}秒..."
            sleep $delay
        fi
    done <<< "$(echo "$steps" | jq -c '.[]')"

    if [ "$success" = true ]; then
        echo ""
        echo "✅ 工作流执行成功"
    else
        echo ""
        echo "❌ 工作流执行失败（在步骤 $step_num）"
    fi

    echo "📋 日志: $log_file"
}

# 显示工作流详情
show_workflow() {
    local name="$1"
    local file=$(get_workflow_file "$name")

    if [ ! -f "$file" ]; then
        echo "❌ 错误: 工作流不存在"
        exit 1
    fi

    echo "📋 工作流详情: $name"
    echo "===================="
    jq '.' "$file"
}

# 编辑工作流
edit_workflow() {
    local name="$1"
    local file=$(get_workflow_file "$name")

    if [ ! -f "$file" ]; then
        echo "❌ 错误: 工作流不存在"
        exit 1
    fi

    ${EDITOR:-vi} "$file"

    # 更新修改时间
    local current_date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    jq --arg date "$current_date" '.updated_at = $date' "$file" > "$file.tmp"
    mv "$file.tmp" "$file"

    echo "✅ 工作流已更新"
}

# 删除工作流
delete_workflow() {
    local name="$1"
    local file=$(get_workflow_file "$name")

    if [ ! -f "$file" ]; then
        echo "❌ 错误: 工作流不存在"
        exit 1
    fi

    read -p "⚠️  确定要删除工作流 '$name'？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm "$file"
        echo "✅ 工作流已删除"
    else
        echo "已取消"
    fi
}

# 查看工作流日志
show_logs() {
    local name="$1"
    local count=10

    if [ -n "$2" ] && [ "$2" = "-n" ]; then
        count="$3"
    fi

    echo "📋 工作流日志: $name (最近 $count 条)"
    echo "===================================="

    if [ ! -d "$LOG_DIR" ]; then
        echo "还没有日志"
        return
    fi

    local logs=$(ls -t "$LOG_DIR"/${name}_*.log 2>/dev/null | head -n "$count")

    if [ -z "$logs" ]; then
        echo "没有找到日志"
        return
    fi

    for log_file in $logs; do
        local basename=$(basename "$log_file")
        local date=$(echo "$basename" | sed "s/${name}_//" | sed 's/.log//')
        echo ""
        echo "📅 $date"
        echo "-------------------"
        tail -n 20 "$log_file"
        echo ""
    done
}

# 主程序
main() {
    if [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi

    local action="$1"
    shift

    case "$action" in
        list)
            list_workflows
            ;;
        create)
            create_workflow "$@"
            ;;
        run)
            if [ $# -eq 0 ]; then
                echo "❌ 错误: 请指定工作流名称"
                exit 1
            fi
            run_workflow "$@"
            ;;
        show)
            if [ $# -eq 0 ]; then
                echo "❌ 错误: 请指定工作流名称"
                exit 1
            fi
            show_workflow "$@"
            ;;
        edit)
            if [ $# -eq 0 ]; then
                echo "❌ 错误: 请指定工作流名称"
                exit 1
            fi
            edit_workflow "$@"
            ;;
        delete)
            if [ $# -eq 0 ]; then
                echo "❌ 错误: 请指定工作流名称"
                exit 1
            fi
            delete_workflow "$@"
            ;;
        logs)
            if [ $# -eq 0 ]; then
                echo "❌ 错误: 请指定工作流名称"
                exit 1
            fi
            show_logs "$@"
            ;;
        *)
            echo "❌ 错误: 未知动作 '$action'"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
