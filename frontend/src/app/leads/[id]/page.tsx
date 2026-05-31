import { AppShell } from "@/components/app-shell";
import { LeadDetailPage } from "@/components/lead-detail-page";

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <AppShell>
      <LeadDetailPage leadId={id} />
    </AppShell>
  );
}
