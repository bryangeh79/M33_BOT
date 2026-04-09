#!/usr/bin/env python3
"""
检查结算执行情况
"""

import sqlite3
import os

def check_settlement_execution():
    print("=== 结算执行情况检查 ===")
    
    db_path = 'data/m33_lotto.db'
    if not os.path.exists(db_path):
        print("❌ 数据库不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 检查settlement_runs表的最新记录
    print("\n1. settlement_runs表状态:")
    cursor.execute('''
        SELECT COUNT(*) as total_count,
               COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
               COUNT(CASE WHEN status != 'completed' THEN 1 END) as other_status_count
        FROM settlement_runs
    ''')
    total, completed, other = cursor.fetchone()
    print(f"   总记录: {total}")
    print(f"   已完成: {completed}")
    print(f"   其他状态: {other}")
    
    # 2. 检查settlement_results表
    print("\n2. settlement_results表状态:")
    try:
        cursor.execute("SELECT COUNT(*) FROM settlement_results")
        count = cursor.fetchone()[0]
        print(f"   记录数: {count}")
        
        if count > 0:
            cursor.execute("SELECT MIN(settlement_date), MAX(settlement_date) FROM settlement_results")
            min_date, max_date = cursor.fetchone()
            print(f"   最早结算: {min_date}")
            print(f"   最新结算: {max_date}")
    except Exception as e:
        print(f"   ❌ 查询错误 (可能表不存在): {e}")
    
    # 3. 检查是否有结算相关的错误或日志
    print("\n3. 检查app.log中的结算相关记录:")
    log_file = 'app.log'
    if os.path.exists(log_file):
        try:
            # 读取最后1000行，查找结算相关日志
            with open(log_file, 'r') as f:
                lines = f.readlines()[-1000:]
                
            settlement_lines = [l for l in lines if 'settle' in l.lower() or '结算' in l]
            error_lines = [l for l in lines if 'ERROR' in l and ('settle' in l.lower() or '结算' in l)]
            
            print(f"   找到 {len(settlement_lines)} 个结算相关日志")
            print(f"   找到 {len(error_lines)} 个结算相关错误")
            
            if error_lines:
                print("   最近结算错误:")
                for err in error_lines[-3:]:
                    print(f"     {err.strip()}")
        except Exception as e:
            print(f"   ❌ 读取日志错误: {e}")
    else:
        print("   ⚠️ 日志文件不存在")
    
    # 4. 手动测试结算查询
    print("\n4. 手动测试2026-04-07 MB结算条件:")
    
    # 检查开奖结果
    cursor.execute('''
        SELECT id, status, fetched_at 
        FROM draw_results 
        WHERE draw_date = '2026-04-07' AND region_code = 'MB'
    ''')
    draw_result = cursor.fetchone()
    
    if draw_result:
        draw_id, status, fetched = draw_result
        print(f"   开奖结果: ID={draw_id}, 状态={status}, 获取时间={fetched}")
        
        if status != 'available':
            print(f"   ❌ 问题: 开奖结果状态不是'available'")
        else:
            print(f"   ✅ 开奖结果可用")
    else:
        print("   ❌ 问题: 未找到开奖结果")
    
    # 检查投注
    cursor.execute('''
        SELECT COUNT(*) 
        FROM bet_items bi
        INNER JOIN bet_batches bb ON bb.id = bi.batch_id
        WHERE bb.bet_date = '2026-04-07' 
          AND bi.region_group = 'MB'
          AND bi.status = 'accepted'
          AND bb.status = 'accepted'
    ''')
    bet_count = cursor.fetchone()[0]
    print(f"   可结算投注项: {bet_count}")
    
    # 检查是否已有结算记录
    cursor.execute('''
        SELECT id, status, total_bets, total_payout
        FROM settlement_runs 
        WHERE draw_date = '2026-04-07' AND region_group = 'MB'
    ''')
    existing_settlement = cursor.fetchone()
    
    if existing_settlement:
        s_id, s_status, s_bets, s_payout = existing_settlement
        print(f"   已有结算记录: ID={s_id}, 状态={s_status}")
        print(f"     投注数: {s_bets}, 派彩: {s_payout}")
        
        if s_bets == 0 and bet_count > 0:
            print(f"   ⚠️ 问题: 结算记录显示0投注，但实际有{bet_count}个投注")
    else:
        print("   ✅ 无现有结算记录")
    
    # 5. 检查settlement_runs表的创建时间
    print("\n5. settlement_runs表时间线:")
    cursor.execute('''
        SELECT draw_date, region_group, status, created_at
        FROM settlement_runs 
        ORDER BY created_at DESC
        LIMIT 5
    ''')
    recent_settlements = cursor.fetchall()
    
    if recent_settlements:
        print("   最近5次结算:")
        for date, region, status, created in recent_settlements:
            print(f"     {date} {region}: {status} (创建于: {created})")
    else:
        print("   无结算记录")
    
    conn.close()
    
    print("\n=== 分析总结 ===")
    
    if bet_count > 0 and draw_result and draw_result[1] == 'available' and not existing_settlement:
        print("✅ 所有结算条件满足，但未执行结算")
        print("   可能原因:")
        print("   1. 结算需要手动触发")
        print("   2. 自动结算功能未启用")
        print("   3. 结算代码有bug")
    elif existing_settlement:
        print("⚠️ 已有结算记录，但可能不完整")
    else:
        print("❓ 其他情况，需要进一步检查")

if __name__ == "__main__":
    check_settlement_execution()