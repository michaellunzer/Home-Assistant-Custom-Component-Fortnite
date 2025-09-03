#!/usr/bin/env python3
"""Test script for Fortnite API connection."""

import sys
from fortnite_python import Fortnite
from fortnite_python.domain import Mode, Platform

def test_fortnite_api():
    """Test the Fortnite API with sample data."""
    print("🎮 Testing Fortnite API Connection...")
    
    # You'll need to replace this with your actual API key
    api_key = input("Enter your Fortnite Tracker API key: ").strip()
    if not api_key:
        print("❌ No API key provided")
        return False
    
    player_id = input("Enter your player ID (e.g., Captain_Crunch88): ").strip()
    if not player_id:
        print("❌ No player ID provided")
        return False
    
    platform_str = input("Enter platform (pc, xbox, psn, switch, kbm): ").strip().lower()
    if platform_str not in ["pc", "xbox", "psn", "switch", "kbm"]:
        print("❌ Invalid platform")
        return False
    
    mode_str = input("Enter game mode (SOLO, DUO, SQUAD): ").strip().upper()
    if mode_str not in ["SOLO", "DUO", "SQUAD"]:
        print("❌ Invalid game mode")
        return False
    
    try:
        print(f"\n🔍 Testing connection for {player_id} on {platform_str} ({mode_str})...")
        
        # Create Fortnite API instance
        game = Fortnite(api_key)
        
        # Map platform names to fortnite-python Platform enum
        platform_mapping = {
            "pc": Platform.PC,
            "xbox": Platform.XBOX,
            "psn": Platform.PSN,
            "switch": Platform.GAMEPAD,  # Nintendo Switch uses GAMEPAD in fortnite-python
            "kbm": Platform.KBM
        }
        
        platform = platform_mapping[platform_str]
        mode = Mode[mode_str]
        
        # Get player data
        player = game.player(player_id, platform)
        print("✅ Player found!")
        
        # Get stats
        stats = player.get_stats(mode)
        print("✅ Stats retrieved successfully!")
        
        # Display some stats
        print(f"\n📊 Sample Stats for {player_id}:")
        print(f"  Kills: {stats.kills}")
        print(f"  Matches: {stats.matches}")
        print(f"  Win Ratio: {stats.win_ratio}")
        print(f"  K/D Ratio: {stats.kd}")
        print(f"  Top 1: {stats.top1}")
        print(f"  Top 3: {stats.top3}")
        print(f"  Top 5: {stats.top5}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_fortnite_api()
    if success:
        print("\n🎉 Fortnite API test successful!")
        print("Your integration should work with these credentials.")
    else:
        print("\n💥 Fortnite API test failed!")
        print("Check your API key and player ID.")
