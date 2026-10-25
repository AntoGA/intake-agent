import json
import unittest
import core
import test_core


class WorkerLeaseTests(unittest.TestCase):
    setUp = test_core.Tests.setUp
    tearDown = test_core.Tests.tearDown
    def test_stale_worker_cannot_overwrite_newer_result(self):
        ident = core.ingest('form', 'lease', 'x', 'request')
        def stale(row):
            with core.connect() as c:
                c.execute("UPDATE leads SET attempts=2,status='review',draft=? WHERE id=?",
                          (json.dumps({'draft': 'newer'}), ident))
            return {'summary': 'old', 'draft': 'old'}
        core.process_one(stale)
        with core.connect() as c:
            row = c.execute('SELECT * FROM leads WHERE id=?', (ident,)).fetchone()
            self.assertEqual(json.loads(row['draft']), {'draft': 'newer'})
            self.assertEqual(c.execute("SELECT count(*) FROM events WHERE event='draft_ready'").fetchone()[0], 0)

    def test_stale_failure_cannot_requeue_approved_lead(self):
        ident = core.ingest('form', 'lease', 'x', 'request')
        def stale(row):
            with core.connect() as c:
                c.execute("UPDATE leads SET attempts=2,status='approved' WHERE id=?", (ident,))
            raise TimeoutError()
        core.process_one(stale)
        with core.connect() as c:
            self.assertEqual(c.execute('SELECT status FROM leads WHERE id=?', (ident,)).fetchone()[0], 'approved')

    def test_core_rejects_blank_request(self):
        with self.assertRaises(ValueError):
            core.ingest('form', 'blank', 'x', '   ')


class AuthenticationTests(unittest.TestCase):
    def test_non_ascii_header_is_rejected(self):
        import os
        from unittest.mock import patch
        from fastapi import HTTPException
        from app import auth, ingest_auth
        with patch.dict(os.environ, {'ADMIN_TOKEN': 'a'*40, 'INGEST_TOKEN': 'i'*40}):
            for check in (auth, ingest_auth):
                with self.assertRaises(HTTPException) as error:
                    check('Bearer неверный')
                self.assertEqual(error.exception.status_code, 401)

    def test_blank_api_fields_are_rejected(self):
        from app import Lead
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            Lead(external_id='id', contact='email', text='   ')
