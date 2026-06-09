'use client';
import usePageTitle from '@/src/hooks/usePageTitle';
import Footer from '@/src/components/Footer';
import { LandingHero, FeatureGrid, TemplatePreview, PricingSection, CTASection, AboutSection } from './components/LandingSections';

export default function Landing() {
    usePageTitle('Automated Academic Manuscript Formatter');

    return (
        <>
            <LandingHero />
            <FeatureGrid />
            <TemplatePreview />
            <PricingSection />
            <CTASection />
            <AboutSection />
            <Footer variant="landing" />
        </>
    );
}
