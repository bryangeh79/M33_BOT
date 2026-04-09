#!/usr/bin/env python3
"""
分析结算积压原因
"""

import sqlite3
import os

def analyze_settlement_backlog():
    print("=== 结算积压分析 ===")
    
    db_path = 'data/m33_lotto.db'
    if not os.path.exists(db_path):
        print("❌ 数据库不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 分析每个区域的结算情况
    regions = ['MB', 'MN', 'MT']
    
    for region in regions:
        print(f"\n--- {region} 区域分析 ---")
        
        # 1. 检查最新开奖结果
        cursor.execute('''
            SELECT draw_date, status, fetched_at
            FROM draw_results 
            WHERE region_code = ?
            ORDER BY draw_date DESC
            LIMIT 3
        ''', (region,))
        
        latest_draws = cursor.fetchall()
        print(f"最新开奖结果:")
        for date, status, fetched in latest_draws:
            print(f"  {date}: {status} (获取于: {fetched})")
        
        # 2. 检查最新结算
        cursor.execute('''
            SELECT draw_date, status, total_bets, total_payout
            FROM settlement_runs 
            WHERE region_group = ?
            ORDER BY draw_date DESC
            LIMIT 3
        ''', (region,))
        
        latest_settlements = cursor.fetchall()
        print(f"最新结算:")
        if latest_settlements:
            for date, status, bets, payout in latest_settlements:
                print(f"  {date}: {status}, {bets}投注, 派彩{payout}")
        else:
            print("  无结算记录")
        
        # 3. 检查待结算投注
        cursor.execute('''
            SELECT bb.bet_date, COUNT(*) as bet_count, 
                   SUM(CAST(bb.batch_total as INTEGER)) as total_amount
            FROM bet_batches bb
            LEFT JOIN settlement_runs sr ON bb.bet_date = sr.draw_date AND bb.region_group = sr.region_group
            WHERE bb.region_group = ?
            AND bb.status = 'accepted'
            AND sr.id IS NULL  -- 未结算
            GROUP BY bb.bet_date
            ORDER BY bb.bet_date DESC
        ''', (region,))
        
        pending_bets = cursor.fetchall()
        
        if pending_bets:
            print(f"待结算投注 ({len(pending_bets)}天):")
            for date, count, amount in pending_bets:
                print(f"  {date}: {count}个投注, 总金额{amount or 0}")
                
                # 检查这一天是否有开奖结果
                cursor.execute('''
                    SELECT status FROM draw_results 
                    WHERE draw_date = ? AND region_code = ?
                ''', (date, region))
                
                draw_result = cursor.fetchone()
                if draw_result:
                    print(f"    开奖结果: {draw_result[0]}")
                    
                    # 如果开奖结果可用但未结算，这是问题！
                    if draw_result[0] == 'available':
                        print(f"    ⚠️ 问题: 有开奖结果但未结算!")
                else:
                    print(f"    开奖结果: 不存在")
        else:
            print("✅ 无待结算投注")
    
    # 4. 总体分析
    print("\n=== 总体分析 ===")
    
    # 检查哪些日期有投注但无开奖结果
    cursor.execute('''
        SELECT DISTINCT bb.bet_date, bb.region_group
        FROM bet_batches bb
        LEFT JOIN draw_results dr ON bb.bet_date = dr.draw_date AND bb.region_group = dr.region_code
        WHERE bb.status = 'accepted'
        AND dr.id IS NULL
        ORDER BY bb.bet_date DESC
        LIMIT 10
    ''')
    
    missing_draws = cursor.fetchall()
    
    if missing_draws:
        print("❌ 有投注但无开奖结果的日期:")
        for date, region in missing_draws:
            print(f"  {date} {region}")
    else:
        print("✅ 所有投注都有对应的开奖结果")
    
    # 检查哪些日期有开奖结果但未结算
    cursor.execute('''
        SELECT DISTINCT dr.draw_date, dr.region_code, dr.status
        FROM draw_results dr
        LEFT JOIN settlement_runs sr ON dr.draw_date = sr.draw_date AND dr.region_code = sr.region_group
        WHERE dr.status = 'available'
        AND sr.id IS NULL
        ORDER BY dr.draw_date DESC
        LIMIT 10
    ''')
    
    unsetted_draws = cursor.fetchall()
    
    if unsetted_draws:
        print("\n⚠️ 有开奖结果但未结算的日期:")
        for date, region, status in unsetted_draws:
            print(f"  {date} {region}: {status}")
            
            # 检查这一天是否有投注
            cursor.execute('''
                SELECT COUNT(*) FROM bet_batches 
                WHERE bet_date = ? AND region_group = ? AND status = 'accepted'
            ''', (date, region))
            
            bet_count = cursor.fetchone()[0]
            if bet_count > 0:
                print(f"    有 {bet_count} 个投注需要结算")
            else:
                print(f"    无投注（正常）")
    else:
        print("✅ 所有可用开奖结果都已结算")
    
    conn.close()

if __name__ == "__main__":
    analyze_settlement_backlog()