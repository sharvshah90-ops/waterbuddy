"""Run: python -m unittest -v test_waterbuddy.py"""
import unittest
from hydration import *

class Calculations(unittest.TestCase):
    def test_empty_half_complete_over_goal(self):
        for total,remaining,pct,fill in [(0,2000,0,0),(1000,1000,50,.5),(1500,500,75,.75),(2000,0,100,1),(2250,0,112.5,1)]:
            p=progress(total,2000)
            self.assertEqual((p['remaining'],p['percent'],p['fill']),(remaining,pct,fill))
    def test_invalid_goals(self):
        for goal in [0,-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError): progress(0,goal)
    def test_exact_milestone_boundaries(self):
        self.assertEqual([milestone(p)[0] for p in [0,49.9,50,74.9,75,99.9,100,120]],
                         ['ready','smile','wave','wave','cheer','cheer','complete','complete'])
    def test_container_estimates(self):
        self.assertEqual(container_amount(1000,.5),500)
        self.assertEqual(container_amount(300,.25),75)
        self.assertEqual(container_amount(250,.25),63)
    def test_logging_and_undo(self):
        m=new_model('2026-10-28')
        add_water(m,250,'09:00');add_water(m,500,'10:00')
        self.assertEqual(current(m)['total'],750)
        undo(m); self.assertEqual(current(m)['total'],250)
    def test_invalid_amounts_leave_state_unchanged(self):
        m=new_model('2026-10-28')
        for amount in [0,-10,2001,1.5,True,'250',float('nan'),float('inf')]:
            with self.assertRaises(ValueError): add_water(m,amount,'09:00')
        self.assertEqual(current(m)['total'],0)
    def test_reset_preserves_prior_days_and_settings(self):
        m=new_model('2026-10-27');add_water(m,1000,'09:00')
        ensure_day(m,'2026-10-28');add_water(m,250,'09:00');reset_today(m)
        self.assertEqual(current(m)['total'],0)
        self.assertEqual(day_total(m['days']['2026-10-27']),1000)
        self.assertEqual(m['goal'],2250)
    def test_real_calendar_streaks_and_gaps(self):
        m=new_model('2026-10-25');m['goal']=1000
        for d in ['2026-10-25','2026-10-26','2026-10-28']:
            ensure_day(m,d);add_water(m,1000,'09:00')
        self.assertEqual(statistics(m)['best'],2)
        self.assertEqual(statistics(m)['streak'],1)
    def test_points_capped_and_undo_recalculates(self):
        m=new_model('2026-10-28');m['goal']=1000;ensure_day(m,m['day'])
        add_water(m,1000,'09:00');add_water(m,1000,'10:00')
        self.assertEqual(statistics(m)['points'],125)
        undo(m);self.assertEqual(statistics(m)['points'],125)
        undo(m);self.assertEqual(statistics(m)['points'],0)
    def test_rollover_preserves_history_and_no_fake_day(self):
        m=new_model('2026-10-28');add_water(m,250,'23:59')
        self.assertTrue(ensure_day(m,'2026-10-29'))
        self.assertEqual(current(m)['total'],0)
        self.assertFalse(ensure_day(m,'2026-10-29'))
        self.assertEqual(len(m['days']),2)
    def test_week_has_seven_dates_without_inventing_records(self):
        rows=weekly(new_model('2026-10-28'))
        self.assertEqual(len(rows),7)
        self.assertEqual(rows[0]['Date'],'2026-10-22')
        self.assertEqual(rows[0]['Status'],'No record')
        self.assertIsNone(rows[0]['Goal ml'])

if __name__=='__main__': unittest.main()
