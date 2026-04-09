#!/usr/bin/env python3
"""
调试数据库错误
"""

import os
import sys
import traceback

# 设置环境变量
os.environ['DB_PATH'] = 'data/test_debug.db'
os.environ['BOT_TOKEN'] = 'test_token'

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("测试数据库初始化...")

try:
    # 测试1: init_database
    print("\n1. 测试init_database()...")
    from src.modules.bet.services.bet_message_service import init_database
    init_database()
    print("✅ init_database() 成功")
except Exception as e:
    print(f"❌ init_database() 失败: {e}")
    traceback.print_exc()

try:
    # 测试2: admin_auth_service
    print("\n2. 测试admin_auth_service...")
    from src.modules.admin.services.admin_auth_service import AdminAuthService
    service = AdminAuthService()
    service.init_and_sync()
    print("✅ admin_auth_service 成功")
except Exception as e:
    print(f"❌ admin_auth_service 失败: {e}")
    traceback.print_exc()

try:
    # 测试3: admin_settings_service
    print("\n3. 测试admin_settings_service...")
    from src.modules.admin.services.admin_settings_service import AdminSettingsService
    service = AdminSettingsService()
    service.init_and_sync()
    print("✅ admin_settings_service 成功")
except Exception as e:
    print(f"❌ admin_settings_service 失败: {e}")
    traceback.print_exc()

try:
    # 测试4: agent_customer_repository
    print("\n4. 测试agent_customer_repository...")
    from src.modules.customer.repositories.agent_customer_repository import AgentCustomerRepository
    repo = AgentCustomerRepository()
    repo.init_table()
    print("✅ agent_customer_repository 成功")
except Exception as e:
    print(f"❌ agent_customer_repository 失败: {e}")
    traceback.print_exc()

try:
    # 测试5: user_preference_repository
    print("\n5. 测试user_preference_repository...")
    from src.modules.customer.repositories.user_preference_repository import UserPreferenceRepository
    repo = UserPreferenceRepository()
    repo.init_table()
    print("✅ user_preference_repository 成功")
except Exception as e:
    print(f"❌ user_preference_repository 失败: {e}")
    traceback.print_exc()

print("\n✅ 所有测试完成")