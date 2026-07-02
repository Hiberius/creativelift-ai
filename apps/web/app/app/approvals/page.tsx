import { AppShell } from "@/components/app-shell";
import { ApprovalsManager } from "@/components/approvals-manager";

export const metadata = { title: "Approvals" };

export default function ApprovalsPage() {
  return (
    <AppShell title="Approval Queue">
      <ApprovalsManager />
    </AppShell>
  );
}
