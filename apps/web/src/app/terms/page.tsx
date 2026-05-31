import { TopBar } from "@/components/TopBar";
import { SiteFooter } from "@/components/SiteFooter";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Terms & Conditions — DoclingRAG",
  description: "Terms of use for the DoclingRAG PDF parsing playground and related services.",
};

export default function TermsPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[var(--background)]">
      <TopBar />
      <article className="mx-auto max-w-3xl flex-1 px-4 py-12 text-sm leading-relaxed text-[var(--foreground)]">
        <h1 className="mb-4 text-2xl font-semibold">Terms &amp; Conditions</h1>
        <p className="mb-6 text-[var(--muted)]">
          <strong>Effective date:</strong> May 31, 2026 ·{" "}
          <strong>Last updated:</strong> May 31, 2026
        </p>

        <p className="mb-4">
          These Terms &amp; Conditions (“Terms”) govern access to and use of <strong>DoclingRAG</strong>{" "}
          (“Service”), including the website, APIs, and related materials, operated by{" "}
          <strong>Chaitanya Prabuddha</strong> (“Operator”, “we”, “us”). The software is also
          available under the GNU Affero General Public License v3.0 (“AGPL-3.0”) for self-hosting.
        </p>
        <p className="mb-4 font-medium">
          BY ACCESSING OR USING THE SERVICE, YOU AGREE TO THESE TERMS. IF YOU DO NOT AGREE, DO NOT
          USE THE SERVICE.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">1. Eligibility</h2>
        <p className="mb-4">
          You must be at least 18 years old (or the age of majority in your jurisdiction) and have
          legal capacity to enter a binding agreement. You represent that your use complies with all
          applicable laws where you are located and where data is processed.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">2. The Service</h2>
        <p className="mb-4">
          DoclingRAG converts PDF documents into Markdown, JSONL chunks, and related outputs using
          automated layout parsing and optional OCR. Output may be incomplete, inaccurate, or
          unsuitable for your purpose. The Service is a <strong>technical tool only</strong> — not
          legal, financial, medical, or professional advice.
        </p>
        <p className="mb-4">
          You must independently verify all output before relying on it for decisions affecting
          rights, safety, money, health, or compliance.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">3. No warranties</h2>
        <p className="mb-4 uppercase">
          THE SERVICE AND ALL OUTPUT ARE PROVIDED “AS IS” AND “AS AVAILABLE” WITHOUT WARRANTIES OF
          ANY KIND, WHETHER EXPRESS, IMPLIED, OR STATUTORY, INCLUDING MERCHANTABILITY, FITNESS FOR A
          PARTICULAR PURPOSE, TITLE, NON-INFRINGEMENT, ACCURACY, AND QUIET ENJOYMENT. WE DO NOT
          WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED, ERROR-FREE, SECURE, OR FREE OF HARMFUL
          COMPONENTS.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">4. Limitation of liability</h2>
        <p className="mb-4 uppercase">
          TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL THE OPERATOR,
          CONTRIBUTORS, AFFILIATES, OR SUPPLIERS BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL,
          CONSEQUENTIAL, EXEMPLARY, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS, REVENUE, DATA,
          GOODWILL, BUSINESS INTERRUPTION, OR PROCUREMENT OF SUBSTITUTE SERVICES, ARISING FROM OR
          RELATED TO THE SERVICE OR THESE TERMS, WHETHER BASED ON WARRANTY, CONTRACT, TORT
          (INCLUDING NEGLIGENCE), STRICT LIABILITY, OR ANY OTHER THEORY, EVEN IF ADVISED OF THE
          POSSIBILITY OF SUCH DAMAGES.
        </p>
        <p className="mb-4 uppercase">
          TO THE FULLEST EXTENT PERMITTED BY LAW, OUR TOTAL AGGREGATE LIABILITY FOR ALL CLAIMS
          ARISING OUT OF OR RELATING TO THE SERVICE IN ANY TWELVE (12) MONTH PERIOD SHALL NOT EXCEED
          THE GREATER OF (A) ONE HUNDRED U.S. DOLLARS (USD $100) OR (B) THE AMOUNT YOU PAID US FOR
          THE SERVICE IN THAT PERIOD (TYPICALLY ZERO FOR FREE USE).
        </p>
        <p className="mb-4">
          Some jurisdictions do not allow exclusion of certain damages or liability caps; in those
          jurisdictions, our liability is limited to the maximum extent permitted by law.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">5. Indemnification</h2>
        <p className="mb-4">
          You agree to <strong>defend, indemnify, and hold harmless</strong> the Operator,
          contributors, and affiliates from and against any claims, damages, losses, liabilities,
          costs, and expenses (including reasonable attorneys&apos; fees) arising out of or related
          to: (a) your use of the Service; (b) PDFs, URLs, or content you submit; (c) your output or
          downstream use of output; (d) your violation of these Terms or applicable law; or (e) your
          violation of any third party&apos;s rights. We may assume exclusive defense of any matter
          subject to indemnification at your expense if we choose.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">6. Acceptable use</h2>
        <p className="mb-4">You agree not to:</p>
        <ul className="mb-4 list-disc space-y-2 pl-6">
          <li>Upload unlawful, infringing, defamatory, harassing, or malicious content;</li>
          <li>Process data without proper authorization or legal basis;</li>
          <li>Probe, scan, or attack the Service or circumvent limits;</li>
          <li>Use the Service to build competing datasets or services that violate AGPL or our rights;</li>
          <li>Reverse engineer hosted components except where law expressly permits;</li>
          <li>Overload or disrupt infrastructure.</li>
        </ul>
        <p className="mb-4">
          We may suspend or block access for violations without notice where permitted by law.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">7. Intellectual property</h2>
        <p className="mb-4">
          We retain rights in the Service branding and site content except open-source code licensed
          under AGPL-3.0. You retain rights in PDFs you upload. You grant us a limited,
          non-exclusive license to process your uploads solely to operate the Service.
        </p>
        <p className="mb-4">
          If you believe content on the Service infringes your copyright, contact us with a notice
          including identification of the work, the material, your contact information, a good-faith
          statement, and your signature (DMCA-style notices are welcome where applicable).
        </p>
        <p className="mb-4">
          Self-hosting and modifications must comply with AGPL-3.0. See{" "}
          <Link href="https://github.com/chayprabs/pdf-to-rag-chunks/blob/main/LICENSE" className="text-[var(--accent)] underline">
            LICENSE
          </Link>
          .
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">8. Privacy</h2>
        <p className="mb-4">
          Our{" "}
          <Link href="/privacy" className="text-[var(--accent)] underline">
            Privacy Policy
          </Link>{" "}
          explains how we handle information. It is incorporated into these Terms by reference.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">9. Third-party links and software</h2>
        <p className="mb-4">
          The Service may link to third-party sites or use open-source libraries. We are not
          responsible for third-party content or services. Your use of third-party components is at
          your own risk and subject to their licenses.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">10. Export and sanctions</h2>
        <p className="mb-4">
          You may not use the Service in violation of export control, sanctions, or embargo laws.
          You represent you are not located in, or ordinarily resident in, a country or entity
          subject to comprehensive sanctions where use is prohibited.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">11. Dispute resolution and governing law</h2>
        <p className="mb-4">
          These Terms are governed by the <strong>laws of India</strong>, without regard to conflict-of-law
          rules, except where mandatory consumer protection laws in your country require otherwise.
        </p>
        <p className="mb-4">
          Any dispute arising from these Terms or the Service shall be subject to the exclusive
          jurisdiction of the courts located in <strong>Bangalore, Karnataka, India</strong>, and you
          consent to personal jurisdiction there, except where prohibited by mandatory law in your
          country of residence.
        </p>
        <p className="mb-4">
          <strong>Informal resolution:</strong> Before filing suit, you agree to contact us in good
          faith to seek resolution within thirty (30) days.
        </p>
        <p className="mb-4">
          Where permitted by law, you agree to bring claims only in your individual capacity and not
          as a plaintiff or class member in any class, collective, or representative proceeding.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">12. Force majeure</h2>
        <p className="mb-4">
          We are not liable for failure or delay due to events beyond reasonable control (natural
          disasters, war, labor disputes, internet failures, government actions, etc.).
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">13. Termination</h2>
        <p className="mb-4">
          You may stop using the Service at any time. We may terminate or suspend access at any time
          for any reason. Sections that by nature should survive (limitations, indemnity, governing
          law) survive termination.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">14. General</h2>
        <ul className="mb-4 list-disc space-y-2 pl-6">
          <li>
            <strong>Entire agreement:</strong> These Terms and the Privacy Policy are the entire
            agreement regarding the hosted Service.
          </li>
          <li>
            <strong>Severability:</strong> If any provision is invalid, the rest remains in effect.
          </li>
          <li>
            <strong>No waiver:</strong> Failure to enforce a provision is not a waiver.
          </li>
          <li>
            <strong>Assignment:</strong> We may assign these Terms; you may not without our consent.
          </li>
          <li>
            <strong>Language:</strong> English version controls in case of translation conflicts.
          </li>
        </ul>

        <h2 className="mb-2 mt-8 text-lg font-semibold">15. Contact</h2>
        <p className="mb-4">
          Operator: Chaitanya Prabuddha —{" "}
          <a
            href="https://www.chaitanyaprabuddha.com"
            className="text-[var(--accent)] underline"
            rel="noopener noreferrer"
            target="_blank"
          >
            https://www.chaitanyaprabuddha.com
          </a>
        </p>

        <p className="mt-8 text-[var(--muted)]">
          These Terms are designed to allocate risk for a free, open-source tool. They do not
          guarantee immunity from legal claims anywhere in the world. Consult a qualified attorney
          in your jurisdiction before high-risk or commercial use.
        </p>
      </article>
      <SiteFooter />
    </div>
  );
}
