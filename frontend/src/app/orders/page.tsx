import { AppShell } from "@/components/app-shell";
import { OrdersPage } from "@/components/orders-page";

export default function OrdersRoute() {
  return (
    <AppShell>
      <OrdersPage />
    </AppShell>
  );
}
