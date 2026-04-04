import { Navbar } from '../components/Navbar';
import { HeroSection } from '../components/HeroSection';
import { FeatureSection } from '../components/FeatureSection';
import { HowItWorks } from '../components/HowItWorks';
import { CTASection } from '../components/CTASection';
import { Footer } from '../components/Footer';
import { ChatWidget } from '../components/ChatWidget';

export function LandingPage() {
    return (
        <div className="min-h-screen bg-cyber-dark text-white overflow-x-hidden">
            <Navbar />

            <div className="pt-[72px]">
                <HeroSection />
                <FeatureSection />
                <HowItWorks />
                <CTASection />
                <Footer />
            </div>

            <ChatWidget />
        </div>
    );
}
