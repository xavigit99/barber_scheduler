import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.handlers.stats.tenant_stats_handler import TenantStatsHandler
from backend.application.queries.tenant_stats_query import TenantStatsQuery
from backend.core.appointment import Appointment
from backend.core.service import Service


class TenantStatsHandlerTestCase(unittest.IsolatedAsyncioTestCase):

    def _make_service(self, price: float) -> MagicMock:
        svc = MagicMock(spec=Service)
        svc.preco = price
        return svc

    def _make_appointment(self, service_id: int) -> MagicMock:
        appt = MagicMock(spec=Appointment)
        appt.service_id = service_id
        return appt

    async def test_counts_are_returned(self):
        db = MagicMock()

        scalar_qb = MagicMock()
        scalar_qb.filter.return_value = scalar_qb
        scalar_qb.scalar.return_value = 3

        list_qb = MagicMock()
        list_qb.filter.return_value = list_qb
        list_qb.all.return_value = []

        service_lookup = MagicMock()
        service_lookup.filter.return_value = service_lookup
        service_lookup.first.return_value = None

        call_count = [0]

        def query_side_effect(model):
            call_count[0] += 1
            if call_count[0] <= 3:
                return scalar_qb
            elif call_count[0] == 4:
                return list_qb
            elif call_count[0] == 5:
                return scalar_qb
            return service_lookup

        db.query.side_effect = query_side_effect

        handler = TenantStatsHandler(db)
        result = await handler.handle(TenantStatsQuery(tenant_id=1))

        self.assertIn("barbers", result)
        self.assertIn("clients", result)
        self.assertIn("services", result)
        self.assertIn("appointments_month", result)
        self.assertIn("revenue_month", result)

    async def test_revenue_sums_service_prices(self):
        db = MagicMock()

        appt1 = self._make_appointment(service_id=10)
        appt2 = self._make_appointment(service_id=20)

        scalar_qb = MagicMock()
        scalar_qb.filter.return_value = scalar_qb
        scalar_qb.scalar.return_value = 0

        list_qb = MagicMock()
        list_qb.filter.return_value = list_qb
        list_qb.all.return_value = [appt1, appt2]

        svc1 = self._make_service(50.0)
        svc2 = self._make_service(30.0)

        lookup_qb = MagicMock()
        lookup_qb.filter.return_value = lookup_qb
        lookup_qb.first.side_effect = [svc1, svc2]

        call_count = [0]

        def query_side_effect(model):
            call_count[0] += 1
            if call_count[0] <= 3:
                return scalar_qb
            elif call_count[0] == 4:
                return list_qb
            elif call_count[0] == 5:
                return scalar_qb
            return lookup_qb

        db.query.side_effect = query_side_effect

        handler = TenantStatsHandler(db)
        result = await handler.handle(TenantStatsQuery(tenant_id=1))

        self.assertAlmostEqual(result["revenue_month"], 80.0)
        self.assertEqual(result["appointments_month"], 2)


if __name__ == "__main__":
    unittest.main()
