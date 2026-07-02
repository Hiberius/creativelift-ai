import { AppShell } from "@/components/app-shell";
import { OnboardingManager } from "@/components/onboarding-manager";

export const metadata = { title: "Onboarding" };

export default function OnboardingPage() {
  return (
    <AppShell title="Onboarding">
      <OnboardingManager />
    </AppShell>
  );
}
