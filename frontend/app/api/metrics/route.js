import { NextResponse } from 'next/server';

export async function GET() {
    // In a real scenario, this would aggregate data from Supabase or your backend metrics.
    // For now, we simulate dynamic numbers returned from an API.

    // Create some slight natural variation to simulate a live growing ecosystem
    const baseResearchers = 25000;
    const baseTemplates = 1000;
    const baseUniversities = 50;

    // Add artificial live growth based on time (grows slightly every day)
    const timeGrowth = Math.floor((Date.now() - new Date('2024-01-01').getTime()) / (1000 * 60 * 60 * 24));

    return NextResponse.json({
        researchers: baseResearchers + (timeGrowth * 2),
        templates: baseTemplates + Math.floor(timeGrowth / 10),
        universities: baseUniversities + Math.floor(timeGrowth / 30),
    });
}
