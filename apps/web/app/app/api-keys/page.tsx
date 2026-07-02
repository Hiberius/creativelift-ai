import { AppShell } from "@/components/app-shell";
import { ApiKeysManager } from "@/components/api-keys-manager";

export const metadata = { title: "API Keys" };

export default function ApiKeysPage() {
  return (
    <AppShell title="API Keys">
      <ApiKeysManager />
    </AppShell>
  );
}
