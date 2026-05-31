import { ParsePlayground } from "@/components/ParsePlayground";
import { SeoBar } from "@/components/SeoBar";
import { SiteFooter } from "@/components/SiteFooter";
import { TopBar } from "@/components/TopBar";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <TopBar />
      <SeoBar />
      <main className="flex-1">
        <ParsePlayground />
      </main>
      <SiteFooter />
    </div>
  );
}
