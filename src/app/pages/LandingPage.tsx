import { Navbar } from '../components/Navbar';
import { HeroSection } from '../components/HeroSection';
import { FeatureSection } from '../components/FeatureSection';
import { HowItWorks } from '../components/HowItWorks';
import { DashboardPreview } from '../components/DashboardPreview';
import { CTASection } from '../components/CTASection';
import { Footer } from '../components/Footer';

export function LandingPage() {
    return (
        <div className="min-h-screen bg-cyber-dark text-white overflow-x-hidden">
            <Navbar />

            {/* Push content below fixed navbar */}
            <div className="pt-[72px]">
                <HeroSection />
                <FeatureSection />
                <HowItWorks />
                <DashboardPreview />
                <CTASection />
                <Footer />
            </div>
        </div>
    );
}
