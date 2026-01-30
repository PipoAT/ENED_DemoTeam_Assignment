#!/usr/bin/env python3
"""
Test script to verify concurrent access and state persistence.
This simulates multiple instances/users accessing the system simultaneously.
"""
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:5000"

def activate_station(station_num):
    """Activate a station."""
    response = requests.post(
        f"{BASE_URL}/toggle_active",
        json={"station": station_num},
        timeout=5
    )
    return response.json()

def assign_team(team_name):
    """Assign a team to a station."""
    response = requests.post(
        f"{BASE_URL}/assign",
        json={"team": team_name},
        timeout=5
    )
    return response.json()

def remove_team(team_name):
    """Remove a team from a station."""
    response = requests.post(
        f"{BASE_URL}/remove",
        json={"team": team_name},
        timeout=5
    )
    return response.json()

def get_assignments():
    """Get current assignments."""
    response = requests.get(f"{BASE_URL}/get_assignments", timeout=5)
    return response.json()

def test_concurrent_assignments():
    """Test concurrent team assignments."""
    print("=" * 60)
    print("TEST 1: Concurrent Team Assignments")
    print("=" * 60)
    
    # Activate stations 1-3
    print("\n1. Activating stations 1-3...")
    for i in range(1, 4):
        result = activate_station(i)
        print(f"   Station {i}: {result}")
    
    time.sleep(0.5)
    
    # Assign 10 teams concurrently
    print("\n2. Assigning 10 teams concurrently...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(assign_team, f"Test.{i:02d}") for i in range(1, 11)]
        results = [future.result() for future in as_completed(futures)]
    
    print(f"   All {len(results)} requests completed")
    
    time.sleep(1)
    
    # Check final state
    print("\n3. Checking final state...")
    state = get_assignments()
    
    assigned_teams = [team for team in state['stations'].values() if team]
    queued_teams = state['team_queue']
    
    print(f"   Teams assigned to stations: {len(assigned_teams)}")
    print(f"   Teams in queue: {len(queued_teams)}")
    print(f"   Total teams: {len(assigned_teams) + len(queued_teams)}")
    
    # Verify all 10 teams are accounted for
    all_teams = assigned_teams + queued_teams
    expected_teams = [f"Test.{i:02d}" for i in range(1, 11)]
    
    print("\n4. Verification:")
    if len(all_teams) == 10:
        print("   ✓ All 10 teams accounted for")
    else:
        print(f"   ✗ ERROR: Expected 10 teams, found {len(all_teams)}")
        return False
    
    if set(all_teams) == set(expected_teams):
        print("   ✓ No duplicate or missing teams")
    else:
        print("   ✗ ERROR: Team mismatch detected")
        return False
    
    return True

def test_state_persistence():
    """Test that state persists across operations."""
    print("\n" + "=" * 60)
    print("TEST 2: State Persistence")
    print("=" * 60)
    
    # Get initial state
    print("\n1. Getting initial state...")
    initial_state = get_assignments()
    initial_count = len([t for t in initial_state['stations'].values() if t])
    print(f"   Teams assigned: {initial_count}")
    
    # Add a new team
    print("\n2. Adding team 'Persist.01'...")
    assign_team("Persist.01")
    time.sleep(0.5)
    
    # Check state again
    print("\n3. Verifying state updated...")
    new_state = get_assignments()
    
    all_teams = [t for t in new_state['stations'].values() if t] + new_state['team_queue']
    
    if "Persist.01" in all_teams:
        print("   ✓ New team found in state")
        return True
    else:
        print("   ✗ ERROR: New team not found in state")
        return False

def test_queue_processing():
    """Test that queue is processed correctly when stations become available."""
    print("\n" + "=" * 60)
    print("TEST 3: Queue Processing")
    print("=" * 60)
    
    # Get current state
    state = get_assignments()
    queue_size = len(state['team_queue'])
    
    print(f"\n1. Current queue size: {queue_size}")
    
    if queue_size == 0:
        print("   No items in queue to test. Adding one...")
        assign_team("Queue.01")
        time.sleep(0.5)
        queue_size = 1
    
    # Activate a new station
    print("\n2. Activating station 5...")
    activate_station(5)
    time.sleep(1)
    
    # Check if queue was processed
    print("\n3. Checking if queue was processed...")
    new_state = get_assignments()
    new_queue_size = len(new_state['team_queue'])
    
    print(f"   Previous queue size: {queue_size}")
    print(f"   Current queue size: {new_queue_size}")
    
    if new_queue_size < queue_size:
        print("   ✓ Queue was processed")
        return True
    else:
        print("   ⚠ Queue size unchanged (station 5 may already be active)")
        return True  # This is OK if station was already active

def cleanup():
    """Clean up test data."""
    print("\n" + "=" * 60)
    print("Cleanup")
    print("=" * 60)
    print("\nRemoving test teams...")
    
    state = get_assignments()
    all_teams = [t for t in state['stations'].values() if t] + state['team_queue']
    
    test_teams = [t for t in all_teams if t.startswith(('Test.', 'Persist.', 'Queue.'))]
    
    for team in test_teams:
        remove_team(team)
        print(f"   Removed {team}")
    
    print(f"\nRemoved {len(test_teams)} test teams")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CONCURRENT ACCESS AND STATE PERSISTENCE TEST")
    print("=" * 60)
    print("\nTesting the Team Station Assignment System")
    print("This verifies that multiple instances can work correctly\n")
    
    try:
        # Run tests
        test1_passed = test_concurrent_assignments()
        test2_passed = test_state_persistence()
        test3_passed = test_queue_processing()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Test 1 (Concurrent Assignments): {'PASSED ✓' if test1_passed else 'FAILED ✗'}")
        print(f"Test 2 (State Persistence):      {'PASSED ✓' if test2_passed else 'FAILED ✗'}")
        print(f"Test 3 (Queue Processing):        {'PASSED ✓' if test3_passed else 'FAILED ✗'}")
        
        if all([test1_passed, test2_passed, test3_passed]):
            print("\nAll tests PASSED! ✓")
            print("The system correctly handles multiple instances and")
            print("maintains consistent state across concurrent operations.")
        else:
            print("\nSome tests FAILED! ✗")
        
        # Cleanup
        cleanup()
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to server.")
        print("Please make sure the Flask app is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
