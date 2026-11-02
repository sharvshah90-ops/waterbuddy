import unittest,json
from planning import plan_slots,reminder_due,restore_backup
from hydration import new_model,add_water
class PlanningTests(unittest.TestCase):
    def test_busy_hours_skipped(self):
        self.assertEqual(plan_slots(8,12,60,[9,10]),[480,660])
    def test_interval(self):
        self.assertEqual(plan_slots(8,9,15,[]),[480,495,510,525])
    def test_no_slots(self): self.assertEqual(plan_slots(8,9,60,[8]),[])
    def test_invalid_day(self):
        with self.assertRaises(ValueError): plan_slots(22,7,60,[])
    def test_reminder_gates(self):
        self.assertTrue(reminder_due(True,12,7,22,[],1000,3600,60,10000,0))
        self.assertFalse(reminder_due(True,12,7,22,[12],1000,3600,60,10000,0))
        self.assertFalse(reminder_due(True,12,7,22,[],0,3600,60,10000,0))
        self.assertFalse(reminder_due(True,12,7,22,[],1000,3600,60,10000,11000))
    def test_backup_roundtrip(self):
        m=new_model('2026-11-02');add_water(m,250,'10:00')
        self.assertEqual(restore_backup(json.dumps(m),'2026-11-02'),m)
    def test_reject_bad_backup(self):
        for raw in ['null','{}','[]','oops']:
            with self.assertRaises(ValueError): restore_backup(raw,'2026-11-02')
    def test_reject_tampered_water(self):
        m=new_model('2026-11-02');m['days'][m['day']]['logs']=[{'ml':-100,'time':'10:00','source':'x'}]
        with self.assertRaises(ValueError):restore_backup(json.dumps(m),'2026-11-02')
if __name__=='__main__':unittest.main()
