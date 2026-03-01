'use client';
import { notFound, useParams } from 'next/navigation';

// The job-step route renders the job-specific variant of each page.
// Each sub-page is the same component as the top-level route,
// but params are injected via the URL (jobId is available via useParams in each child).
import DownloadPage from '@/app/(formatter)/download/page';
import ComparePage from '@/app/(formatter)/compare/page';
import EditPage from '@/app/(formatter)/edit/page';
import ValidationResultsPage from '@/app/(formatter)/results/page';
import PreviewPage from '@/app/(formatter)/preview/page';

export default function JobStepPage() {
    const params = useParams();
    const { step } = params;

    // Strict whitelist exactly as required by DoD
    const allowedSteps = ['download', 'compare', 'edit', 'results', 'preview'];

    if (!allowedSteps.includes(step)) {
        notFound(); // Returns native Next.js 404
    }

    // Render the appropriate component
    switch (step) {
        case 'download':
            return <DownloadPage />;
        case 'compare':
            return <ComparePage />;
        case 'edit':
            return <EditPage />;
        case 'results':
            return <ValidationResultsPage />;
        case 'preview':
            return <PreviewPage />;
        default:
            notFound();
    }
}
