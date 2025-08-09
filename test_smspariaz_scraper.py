"""
Test script for SMS Pariaz scraper
This script tests the smspariaz scraper functionality and displays the results
"""
import json
from datetime import datetime
from utils.smspariaz_scraper import scrape_horses_from_smspariaz


def test_smspariaz_scraper():
    """Test the SMS Pariaz scraper and display results"""
    print("=" * 60)
    print("🏇 TESTING SMS PARIAZ SCRAPER")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        print("🔄 Calling scraper function...")
        races_data = scrape_horses_from_smspariaz()
        
        if not races_data:
            print("❌ No race data returned")
            return False
            
        print(f"✅ Scraper completed successfully!")
        print(f"📊 Number of races found: {len(races_data)}")
        print()
        
        # Display detailed results
        for i, race in enumerate(races_data, 1):
            print(f"🏁 RACE {i}:")
            print(f"   ID: {race.get('id', 'N/A')}")
            print(f"   Name: {race.get('name', 'N/A')}")
            print(f"   Time: {race.get('time', 'N/A')}")
            print(f"   Status: {race.get('status', 'N/A')}")
            print(f"   Number of horses: {len(race.get('horses', []))}")
            
            # Display horses
            horses = race.get('horses', [])
            if horses:
                print("   🐎 Horses:")
                for horse in horses:
                    print(f"      #{horse.get('number', 'N/A')}: {horse.get('name', 'N/A')} "
                          f"(Odds: {horse.get('odds', 'N/A')}, Points: {horse.get('points', 'N/A')})")
            else:
                print("   ⚠️  No horses found in this race")
            print()
        
        # Save results to file for inspection
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_results_smspariaz_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(races_data, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")
        print()
        
        # Validate data structure
        print("🔍 VALIDATING DATA STRUCTURE:")
        validation_passed = True
        
        for i, race in enumerate(races_data):
            race_num = i + 1
            
            # Check required fields
            required_fields = ['id', 'name', 'time', 'horses', 'winner', 'status']
            for field in required_fields:
                if field not in race:
                    print(f"❌ Race {race_num}: Missing required field '{field}'")
                    validation_passed = False
            
            # Check horses structure
            horses = race.get('horses', [])
            for j, horse in enumerate(horses):
                horse_num = j + 1
                horse_required_fields = ['number', 'name', 'odds', 'points']
                for field in horse_required_fields:
                    if field not in horse:
                        print(f"❌ Race {race_num}, Horse {horse_num}: Missing required field '{field}'")
                        validation_passed = False
        
        if validation_passed:
            print("✅ All data structure validations passed!")
        else:
            print("❌ Some data structure validations failed")
            
        print()
        print("=" * 60)
        print("🎯 TEST SUMMARY:")
        print(f"   Scraper Status: {'✅ WORKING' if races_data else '❌ FAILED'}")
        print(f"   Races Retrieved: {len(races_data)}")
        print(f"   Data Validation: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
        print(f"   Results File: {filename}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print("📋 Full traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_smspariaz_scraper()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
        
    input("\nPress Enter to exit...")
