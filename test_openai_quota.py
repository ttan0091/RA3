import os
import sys
from dotenv import load_dotenv
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError

def test_api_quota():
    # 加载 .env 文件
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("未在环境变量或 .env 中找到 OPENAI_API_KEY。")
        sys.exit(1)

    print("正在测试 OpenAI API (密钥以 '...' 结尾: {})".format(api_key[-4:]))
    
    # 获取 BASE_URL 应对可能存在的代理，如果没有则保持为空
    base_url = os.getenv("OPENAI_BASE_URL", os.getenv("OPENAI_API_BASE", None))
    
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
        print(f"检测到 Base URL: {base_url}")
        
    client = OpenAI(**client_kwargs)

    try:
        # 使用 gpt-3.5-turbo 发送最少 token 的请求测试连通性与额度
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=1
        )
        print("✅ 测试成功：API 密钥有效且账号有可用额度。")
        print(f"响应内容: {response.choices[0].message.content}")
    except AuthenticationError as e:
        print(f"❌ 认证失败：API 密钥无效或已被撤销。详细信息: {e}")
    except RateLimitError as e:
        print(f"❌ 额度不足：账号余额可能已耗尽，或触发了速率限制。详细信息: {e}")
    except APIConnectionError as e:
        print(f"❌ 连接失败：无法连接到 OpenAI API。可能需要配置代理。详细信息: {e}")
    except APIError as e:
        print(f"❌ 未知 API 错误: {e}")
    except Exception as e:
        print(f"❌ 发生意外错误: {e}")

if __name__ == "__main__":
    test_api_quota()
