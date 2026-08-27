import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath('.'))

from backend.app import create_app
from backend.models.mock_db import db

app = create_app()
app.config['TESTING'] = True

def test_booking_sheet():
    today_str = datetime.now().strftime("%Y-%m-%d")

    with app.test_client() as client:
        # Login first
        login_res = client.post('/login', data={'username': 'admin', 'password': 'password123'}, follow_redirects=True)
        print("Login status:", login_res.status_code)

        print(f"=== Test 1: Load Full Schedule Matrix for Today ({today_str}) ===")
        res = client.get(f'/api/booking-sheet/matrix?date={today_str}')
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.get_json()
        assert data['success'] == True
        assert 'matrix' in data
        assert len(data['courts']) == 6
        assert len(data['time_slots']) == 19
        print(f"Schedule Matrix loaded: {len(data['time_slots'])} time slots x {len(data['courts'])} courts.")

        
        # Check Court 1 at 09:00 AM is booked for Juan Dela Cruz
        cell_9am = data['matrix']['09:00 AM']['Court 1']
        assert cell_9am['status'] == 'booked', f"Expected booked, got {cell_9am}"
        assert cell_9am['customer_name'] == 'Juan Dela Cruz'
        assert cell_9am['payment_status'] == 'paid'
        print("Matrix cell [09:00 AM, Court 1] PASSED: Juan Dela Cruz — Paid.")

        # Check Court 1 at 06:00 PM is Open Play blocked
        cell_6pm = data['matrix']['06:00 PM']['Court 1']
        assert cell_6pm['status'] == 'open_play', f"Expected open_play, got {cell_6pm}"
        assert 'Prime Evening Open Play' in cell_6pm['title']
        print("Matrix cell [06:00 PM, Court 1] PASSED: Open Play Blocked.")

        print("\n=== Test 2: Save Direct Booking on Vacant Slot (11:00 AM, Court 2) ===")
        save_res = client.post('/api/booking-sheet/save', json={
            'date': today_str,
            'court': 'Court 2',
            'time_slot': '11:00 AM',
            'customer_name': 'Ramon Magsaysay',
            'payment_status': 'unpaid'
        })
        assert save_res.status_code == 200, f"Expected 200, got {save_res.status_code}: {save_res.get_data(as_text=True)}"
        save_data = save_res.get_json()
        assert save_data['success'] == True
        print("Save direct booking PASSED:", save_data['message'])

        # Verify matrix updated
        res2 = client.get(f'/api/booking-sheet/matrix?date={today_str}')
        cell_11am = res2.get_json()['matrix']['11:00 AM']['Court 2']
        assert cell_11am['status'] == 'booked'
        assert cell_11am['customer_name'] == 'Ramon Magsaysay'
        assert cell_11am['payment_status'] == 'unpaid'
        print("Matrix verification after save PASSED: Ramon Magsaysay — Unpaid on Court 2.")

        print("\n=== Test 3: Reject Direct Booking on Open Play Slot (07:00 PM, Court 1) ===")
        conflict_save = client.post('/api/booking-sheet/save', json={
            'date': today_str,
            'court': 'Court 1',
            'time_slot': '07:00 PM',
            'customer_name': 'Illegal Booking',
            'payment_status': 'paid'
        })
        assert conflict_save.status_code == 400
        assert conflict_save.get_json()['success'] == False
        print("Direct booking on Open Play slot rejected PASSED:", conflict_save.get_json()['message'])

        print("\n=== Test 4: Reject Open Play Creation Overlapping Direct Booking ===")
        op_res = client.post('/open-play/sessions/create', json={
            'title': 'Conflicting Open Play',
            'date': today_str,
            'start_time': '08:00 AM',
            'end_time': '11:00 AM',
            'court_count': 2,
            'max_players': 16
        })
        assert op_res.status_code == 400
        assert op_res.get_json()['success'] == False
        print("Open Play creation conflict check PASSED:", op_res.get_json()['message'])

        print("\n=== Test 5: Clear Direct Booking (11:00 AM, Court 2) ===")
        clear_res = client.post('/api/booking-sheet/clear', json={
            'date': today_str,
            'court': 'Court 2',
            'time_slot': '11:00 AM'
        })
        assert clear_res.status_code == 200
        assert clear_res.get_json()['success'] == True
        print("Clear booking PASSED:", clear_res.get_json()['message'])

        print("\nALL 5 MATRIX TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_booking_sheet()
