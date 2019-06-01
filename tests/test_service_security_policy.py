import unittest
from launchkey.exceptions import DuplicateGeoFenceName, DuplicateTimeFenceName
from mock import MagicMock
from ddt import ddt
import pytz
from datetime import time
from launchkey.entities.service import ServiceSecurityPolicy
from launchkey.exceptions import InvalidTimeFenceStartTime, InvalidTimeFenceEndTime, InvalidTimeFenceName, \
    MismatchedTimeFenceTimezones


@ddt
class TestServiceSecurityPolicy(unittest.TestCase):

    def test_defaults(self):
        policy = ServiceSecurityPolicy()
        self.assertIsNone(policy.timefences)
        self.assertIsNone(policy.geofences)
        self.assertIsNone(policy.minimum_amount)
        self.assertIsNone(policy.minimum_requirements)
        self.assertIsNone(policy.jailbreak_protection)

    def test_add_geofence(self):
        policy = ServiceSecurityPolicy()
        latitude = MagicMock(spec=int)
        longitude = MagicMock(spec=int)
        radius = MagicMock(spec=int)
        policy.add_geofence(latitude, longitude, radius, 'a fence')
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors']), 1)
        factor = retrieved['factors'][0]
        self.assertEqual(factor['factor'], 'geofence')
        self.assertEqual(len(factor['attributes']['locations']), 1)
        location = factor['attributes']['locations'][0]
        self.assertEqual(location['latitude'], float(latitude))
        self.assertEqual(location['longitude'], float(longitude))
        self.assertEqual(location['radius'], float(radius))
        # Add a second geofence
        latitude2 = MagicMock(spec=int)
        longitude2 = MagicMock(spec=int)
        radius2 = MagicMock(spec=int)
        policy.add_geofence(latitude2, longitude2, radius2, 'another fence')
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors']), 1)
        factor = retrieved['factors'][0]
        self.assertEqual(factor['factor'], 'geofence')
        self.assertEqual(len(factor['attributes']['locations']), 2)
        location = factor['attributes']['locations'][1]
        self.assertEqual(location['latitude'], float(latitude2))
        self.assertEqual(location['longitude'], float(longitude2))
        self.assertEqual(location['radius'], float(radius2))

    def test_add_duplicate_geofence_name(self):
        policy = ServiceSecurityPolicy()
        policy.add_geofence(1, 1, 1, 'a Fence')
        with self.assertRaises(DuplicateGeoFenceName):
            policy.add_geofence(2, 2, 2, 'A fence')

    def test_add_geofence_with_no_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            ServiceSecurityPolicy().add_geofence(2, 2, 2, None)

    def test_add_timefence_object(self):
        policy = ServiceSecurityPolicy()
        start_time = time(hour=12, minute=30, second=30)
        end_time = time(hour=23, minute=45, second=45)
        policy.add_timefence("Fence 1", start_time, end_time, monday=True, wednesday=True, sunday=True)
        self.assertEqual(len(policy.timefences), 1)
        timefence = policy.timefences[0]

        self.assertIn("Monday", timefence.days)
        self.assertTrue(timefence.monday)

        self.assertNotIn("Tuesday", timefence.days)
        self.assertFalse(timefence.tuesday)

        self.assertIn("Wednesday", timefence.days)
        self.assertTrue(timefence.wednesday)

        self.assertNotIn("Thursday", timefence.days)
        self.assertFalse(timefence.thursday)

        self.assertNotIn("Friday", timefence.days)
        self.assertFalse(timefence.friday)

        self.assertNotIn("Saturday", timefence.days)
        self.assertFalse(timefence.saturday)

        self.assertIn("Sunday", timefence.days)
        self.assertTrue(timefence.sunday)

        self.assertEqual(timefence.start_time, start_time)
        self.assertEqual(timefence.end_time, end_time)
        self.assertEqual(timefence.timezone, "UTC")

    def test_add_multiple_timefences(self):
        policy = ServiceSecurityPolicy()
        self.assertIsNone(policy.timefences)
        start_time = time(hour=12, minute=30, second=30)
        end_time = time(hour=23, minute=45, second=45)
        policy.add_timefence("Fence 1", start_time, end_time, monday=True, wednesday=True,
                             sunday=True)
        self.assertEqual(len(policy.timefences), 1)
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors']), 1)
        factor = retrieved['factors'][0]
        self.assertEqual(factor['factor'], 'timefence')
        self.assertEqual(len(factor['attributes']['time fences']), 1)
        fence = factor['attributes']['time fences'][0]
        self.assertEqual(fence['name'], "Fence 1")
        self.assertEqual(fence['start hour'], 12)
        self.assertEqual(fence['start minute'], 30)
        self.assertEqual(fence['end hour'], 23)
        self.assertEqual(fence['end minute'], 45)
        self.assertEqual(fence['timezone'], "UTC")
        self.assertIn('Monday', fence['days'])
        self.assertIn('Wednesday', fence['days'])
        self.assertIn('Sunday', fence['days'])
        # Add a second timefence
        start_time_2 = time(hour=20, minute=10, second=10)
        end_time_2 = time(hour=22, minute=50, second=20)
        policy.add_timefence("Fence 2", start_time_2, end_time_2, tuesday=True, thursday=True,
                             friday=True,
                             saturday=True)
        self.assertEqual(len(policy.timefences), 2)
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors']), 1)
        factor = retrieved['factors'][0]
        self.assertEqual(factor['factor'], 'timefence')
        self.assertEqual(len(factor['attributes']['time fences']), 2)
        fence = factor['attributes']['time fences'][1]
        self.assertEqual(fence['name'], "Fence 2")
        self.assertEqual(fence['start hour'], 20)
        self.assertEqual(fence['start minute'], 10)
        self.assertEqual(fence['end hour'], 22)
        self.assertEqual(fence['end minute'], 50)
        self.assertEqual(fence['timezone'], "UTC")
        self.assertIn('Tuesday', fence['days'])
        self.assertIn('Thursday', fence['days'])
        self.assertIn('Friday', fence['days'])
        self.assertIn('Saturday', fence['days'])

    def test_add_duplicate_timefence_name(self):
        policy = ServiceSecurityPolicy()
        policy.add_timefence("a Fence", time(), time())
        with self.assertRaises(DuplicateTimeFenceName):
            policy.add_timefence('A fence', time(), time())

    def test_invalid_start_time(self):
        policy = ServiceSecurityPolicy()
        with self.assertRaises(InvalidTimeFenceStartTime):
            policy.add_timefence("A Fence", 'Start Time', time())

    def test_invalid_end_time(self):
        policy = ServiceSecurityPolicy()
        with self.assertRaises(InvalidTimeFenceEndTime):
            policy.add_timefence("A Fence", time(), "End Time")

    def test_mismatched_time_zones(self):
        policy = ServiceSecurityPolicy()
        with self.assertRaises(MismatchedTimeFenceTimezones):
            policy.add_timefence("A Fence", time(), time(tzinfo=pytz.timezone("US/Pacific")))

    def test_add_timefence_timezone(self):
        policy = ServiceSecurityPolicy()
        policy.add_timefence("A Fence", time(tzinfo=pytz.timezone("US/Pacific")),
                             time(tzinfo=pytz.timezone("US/Pacific")))
        self.assertEqual(policy.timefences[0].timezone, "US/Pacific")
        retrieved = policy.get_policy()
        factor = retrieved['factors'][0]
        self.assertEqual(factor['attributes']['time fences'][0]['timezone'], "US/Pacific")

    def test_remove_timefence(self):
        # Create a policy and add two time fences
        policy = ServiceSecurityPolicy()
        policy.add_timefence("my timefence", time(hour=10), time(hour=11))
        policy.add_timefence("my timefence 2", time(hour=12), time(hour=13))
        self.assertEqual(len(policy.timefences), 2)
        retrieved = policy.get_policy()
        factor = retrieved['factors'][0]
        self.assertEqual(len(factor['attributes']['time fences']), 2)

        # Remove the first time fence
        policy.remove_timefence('my timefence')
        self.assertEqual(len(policy.timefences), 1)
        retrieved = policy.get_policy()
        factor = retrieved['factors'][0]

        # Verify the correct time fence was removed
        self.assertEqual(len(factor['attributes']['time fences']), 1)
        self.assertEqual(factor['attributes']['time fences'][0]['name'], "my timefence 2")
        self.assertEqual(factor['attributes']['time fences'][0]['start hour'], 12)
        self.assertEqual(factor['attributes']['time fences'][0]['end hour'], 13)
        self.assertEqual(policy.timefences[0].name, "my timefence 2")
        self.assertEqual(policy.timefences[0].start_time.hour, 12)
        self.assertEqual(policy.timefences[0].end_time.hour, 13)

    def test_remove_last_timefence(self):
        # Create a policy and add two time fences
        policy = ServiceSecurityPolicy()
        policy.add_timefence("my timefence", time(hour=10), time(hour=11))
        # Remove the first time fence
        policy.remove_timefence('my timefence')
        self.assertIsNone(policy.timefences)
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors']), 0)

    def test_remove_invalid_timefence_no_timefences(self):
        policy = ServiceSecurityPolicy()
        with self.assertRaises(InvalidTimeFenceName):
            policy.remove_timefence("Nonexistent Timefence")

    def test_remove_invalid_timefence_existing_timefence(self):
        policy = ServiceSecurityPolicy()
        policy.add_timefence("Existing Timefence", time(), time())
        with self.assertRaises(InvalidTimeFenceName):
            policy.remove_timefence("Nonexistent Timefence")

    def test_remove_partially_invalid_timefence(self):
        policy = ServiceSecurityPolicy()
        policy.add_timefence("name", time(), time())
        policy.timefences.pop()
        with self.assertRaises(InvalidTimeFenceName):
            policy.remove_timefence("name")

    def test_import_timefence_from_policy(self):
        policy = ServiceSecurityPolicy()
        self.assertIsNone(policy.timefences)
        policy.set_policy(
            {
                'minimum_requirements': [],
                'factors': [
                    {
                        'quickfail': False,
                        'priority': 1,
                        'requirement': 'forced requirement',
                        'attributes': {
                            'time fences': [
                                {
                                    'name': 'my timefence',
                                    'days': ['Monday', 'Friday'],
                                    'start minute': 0,
                                    'start hour': 12,
                                    'timezone': 'US/Pacific',
                                    'end hour': 13,
                                    'end minute': 0
                                }
                            ]
                        },
                        'factor': 'timefence'
                    }
                ]
            }
        )
        self.assertIsNotNone(policy.timefences)
        timefence = policy.timefences[0]
        self.assertTrue(timefence.monday)
        self.assertFalse(timefence.tuesday)
        self.assertFalse(timefence.wednesday)
        self.assertFalse(timefence.thursday)
        self.assertTrue(timefence.friday)
        self.assertFalse(timefence.saturday)
        self.assertFalse(timefence.sunday)
        self.assertEqual(timefence.name, 'my timefence')
        self.assertEqual(timefence.start_time, time(hour=12, minute=0, tzinfo=pytz.timezone("US/Pacific")))
        self.assertEqual(timefence.end_time, time(hour=13, minute=0, tzinfo=pytz.timezone("US/Pacific")))
        self.assertEqual(timefence.timezone, "US/Pacific")

    def test_import_geofence_from_policy_does_not_require_name(self):
        policy = ServiceSecurityPolicy()
        self.assertIsNone(policy.timefences)
        policy.set_policy(
            {
                'minimum_requirements': [],
                'factors': [
                    {
                        'quickfail': False,
                        'priority': 1,
                        'requirement': 'forced requirement',
                        'attributes': {
                            'locations': [
                                {
                                    'latitude': 36.15986241774762,
                                    'longitude': -115.15869140624999,
                                    'radius': 20700
                                }
                            ]
                        },
                        'factor': 'geofence'
                    }
                ]
            }
        )
        self.assertEqual(len(policy.geofences), 1)
        geofence = policy.geofences[0]
        self.assertIsNone(geofence.name)
        self.assertEqual(geofence.latitude, 36.15986241774762)
        self.assertEqual(geofence.longitude, -115.15869140624999)
        self.assertEqual(geofence.radius, 20700)
