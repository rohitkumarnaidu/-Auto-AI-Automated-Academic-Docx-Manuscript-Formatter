'use client';
import { useState, useEffect, useCallback, useRef } from 'react';
import usePageTitle from '@/src/hooks/usePageTitle';
import { useToast } from '@/src/context/ToastContext';
import { useUnsavedChanges } from '@/src/hooks/useUnsavedChanges';
import {
    downloadGeneratedDocument,
    generateDocument,
    getGenerationStatus,
    streamGenerationStatus,
} from '@/src/services/api';

const DOC_TYPES = [
    { id: 'academic_paper', label: 'Academic Paper', icon: 'article', description: 'Research paper with abstract, methodology, results, and references.', color: 'from-blue-500 to-blue-700' },
    { id: 'resume', label: 'Resume / CV', icon: 'badge', description: 'Professional CV with education, experience, and skills sections.', color: 'from-emerald-500 to-emerald-700' },
    { id: 'portfolio', label: 'Portfolio', icon: 'folder_special', description: 'Researcher or creative portfolio with projects and publications.', color: 'from-purple-500 to-purple-700' },
    { id: 'report', label: 'Technical Report', icon: 'description', description: 'Structured technical or business report with findings and recommendations.', color: 'from-orange-500 to-orange-700' },
    { id: 'thesis', label: 'Thesis Chapter', icon: 'school', description: 'Thesis or dissertation chapter with structured academic sections.', color: 'from-rose-500 to-rose-700' },
];

const TEMPLATES = [
    { id: 'ieee', name: 'IEEE', category: 'Engineering' },
    { id: 'apa', name: 'APA (7th)', category: 'Social Science' },
    { id: 'acm', name: 'ACM', category: 'Computer Science' },
    { id: 'springer', name: 'Springer', category: 'Science' },
    { id: 'elsevier', name: 'Elsevier', category: 'Science' },
    { id: 'nature', name: 'Nature', category: 'Biology/Science' },
    { id: 'harvard', name: 'Harvard', category: 'General' },
    { id: 'chicago', name: 'Chicago (17th)', category: 'Humanities' },
    { id: 'mla', name: 'MLA (9th)', category: 'Humanities' },
    { id: 'vancouver', name: 'Vancouver', category: 'Medicine' },
    { id: 'numeric', name: 'Numeric', category: 'General' },
    { id: 'none', name: 'None', category: 'Passthrough' },
    { id: 'modern_blue', name: 'Modern Blue', category: 'Custom' },
    { id: 'modern_gold', name: 'Modern Gold', category: 'Custom' },
    { id: 'modern_red', name: 'Modern Red', category: 'Custom' },
    { id: 'resume', name: 'Resume', category: 'Professional' },
    { id: 'portfolio', name: 'Portfolio', category: 'Professional' },
];

const DEFAULT_PAPER_SECTIONS = [
    { name: 'Introduction', include: true },
    { name: 'Literature Review', include: true },
    { name: 'Methodology', include: true },
    { name: 'Results', include: true },
    { name: 'Discussion', include: true },
    { name: 'Conclusion', include: true },
    { name: 'References', include: true },
];

const DEFAULT_RESUME_EDUCATION = [{ institution: '', degree: '', year: '' }];
const DEFAULT_RESUME_EXPERIENCE = [{ company: '', role: '', duration: '', bullets_raw: '' }];

const makeDefaultMetadata = (docType = '') => {
    if (docType === 'resume') {
        return { name: '', email: '', phone: '', linkedin: '', summary: '', skills_raw: '', certifications_raw: '', education: [...DEFAULT_RESUME_EDUCATION], experience: [...DEFAULT_RESUME_EXPERIENCE] };
    }
    return { sections: [...DEFAULT_PAPER_SECTIONS], include_placeholder: true, language: 'english' };
};

const toUiStatus = (status) => {
    const normalized = String(status || '').toUpperCase();
    if (normalized === 'COMPLETED' || normalized === 'COMPLETED_WITH_WARNINGS' || normalized === 'DONE') return 'done';
    if (normalized === 'FAILED' || normalized === 'ERROR') return 'failed';
    if (normalized === 'PENDING') return 'pending';
    return 'processing';
};

function StepDocType({ selected, onSelect }) {
    return (
        <div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">Choose Document Type</h2>
            <p className="text-slate-500 dark:text-gray-400 mb-8">Select the type of document you want to generate.</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {DOC_TYPES.map((docType) => (
                    <button key={docType.id} id={`doc-type-${docType.id}`} onClick={() => onSelect(docType.id)}
                        className={`relative group flex flex-col items-start gap-3 p-5 rounded-2xl border-2 transition-all duration-200 text-left min-h-[120px] ${selected === docType.id
                            ? 'border-primary bg-primary/10 shadow-lg shadow-primary/20'
                            : 'border-glass-border bg-white/5 hover:border-glass-border/50 hover:bg-white/10'
                            }`}>
                        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${docType.color} flex items-center justify-center`}>
                            <span className="material-symbols-outlined text-white text-xl">{docType.icon}</span>
                        </div>
                        <div>
                            <p className="font-semibold text-slate-900 dark:text-slate-100 text-sm">{docType.label}</p>
                            <p className="text-slate-500 dark:text-gray-400 text-xs mt-1 leading-relaxed">{docType.description}</p>
                        </div>
                        {selected === docType.id && <span className="absolute top-3 right-3 material-symbols-outlined text-primary-light text-base">check_circle</span>}
                    </button>
                ))}
            </div>
        </div>
    );
}

function StepTemplate({ selected, onSelect }) {
    const [filter, setFilter] = useState('');
    const [activeCategory, setActiveCategory] = useState('All');
    const categories = ['All', ...new Set(TEMPLATES.map((t) => t.category))];
    const visibleTemplates = TEMPLATES.filter((t) => {
        const matchesCategory = activeCategory === 'All' || t.category === activeCategory;
        const q = filter.toLowerCase();
        return matchesCategory && (t.name.toLowerCase().includes(q) || t.category.toLowerCase().includes(q));
    });

    return (
        <div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">Choose a Template</h2>
            <p className="text-slate-500 dark:text-gray-400 mb-6">Pick the journal or style template for your document.</p>
            <div className="flex flex-col sm:flex-row gap-3 mb-6">
                <input id="template-search" type="text" placeholder="Search templates..." value={filter} onChange={(e) => setFilter(e.target.value)}
                    className="flex-1 bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-2.5 text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-gray-500 text-sm focus:outline-none focus:border-primary transition" />
                <div className="flex gap-2 flex-wrap">
                    {categories.map((cat) => (
                        <button key={cat} onClick={() => setActiveCategory(cat)}
                            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition min-h-[36px] ${activeCategory === cat ? 'bg-blue-600 text-white' : 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-gray-400 hover:bg-slate-200 dark:hover:bg-white/10 hover:text-slate-900 dark:hover:text-white'}`}>
                            {cat}
                        </button>
                    ))}
                </div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {visibleTemplates.map((t) => (
                    <button key={t.id} id={`template-${t.id}`} onClick={() => onSelect(t.id)}
                        className={`flex flex-col items-start gap-1 p-4 rounded-xl border-2 text-left transition-all duration-150 min-h-[72px] ${selected === t.id
                            ? 'border-primary bg-primary/10'
                            : 'border-glass-border bg-white/5 hover:border-glass-border/50 hover:bg-white/8'
                            }`}>
                        <span className={`text-xs font-bold uppercase tracking-wider ${selected === t.id ? 'text-primary-light' : 'text-gray-500'}`}>{t.category}</span>
                        <span className="text-slate-900 dark:text-slate-100 font-semibold text-sm">{t.name}</span>
                        {selected === t.id && <span className="material-symbols-outlined text-primary-light text-sm mt-1">check_circle</span>}
                    </button>
                ))}
            </div>
        </div>
    );
}

function StepMetadata({ docType, metadata, onChange }) {
    const setValue = (key, value) => onChange({ ...metadata, [key]: value });
    const toggleSection = (index) => {
        const sections = [...(metadata.sections || DEFAULT_PAPER_SECTIONS)];
        sections[index] = { ...sections[index], include: !sections[index].include };
        onChange({ ...metadata, sections });
    };
    const updateArrayItem = (key, index, field, value) => {
        const list = [...(metadata[key] || [])];
        list[index] = { ...(list[index] || {}), [field]: value };
        onChange({ ...metadata, [key]: list });
    };
    const addArrayItem = (key, template) => onChange({ ...metadata, [key]: [...(metadata[key] || []), template] });
    const removeArrayItem = (key, index) => {
        const list = [...(metadata[key] || [])];
        list.splice(index, 1);
        onChange({ ...metadata, [key]: list.length ? list : [key === 'education' ? { institution: '', degree: '', year: '' } : { company: '', role: '', duration: '', bullets_raw: '' }] });
    };

    const inputCls = "w-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-3 text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-gray-600 text-sm focus:outline-none focus:border-primary transition";

    if (docType === 'academic_paper' || docType === 'thesis') {
        const sections = metadata.sections || DEFAULT_PAPER_SECTIONS;
        return (
            <div className="space-y-6">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-1">Document Details</h2>
                    <p className="text-slate-500 dark:text-gray-400 text-sm">Fill in the details for your {docType === 'thesis' ? 'thesis chapter' : 'academic paper'}.</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Paper Title *</label>
                        <input id="meta-title" type="text" placeholder="e.g. Deep Learning for Academic Document Formatting" value={metadata.title || ''} onChange={(e) => setValue('title', e.target.value)} className={inputCls} />
                    </div>
                    <div>
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Authors</label>
                        <input id="meta-authors" type="text" placeholder="e.g. John Doe, Jane Smith" value={metadata.authors_raw || ''} onChange={(e) => setValue('authors_raw', e.target.value)} className={inputCls} />
                    </div>
                    <div>
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Affiliation</label>
                        <input id="meta-affiliation" type="text" placeholder="e.g. MIT, Cambridge University" value={metadata.affiliation || ''} onChange={(e) => setValue('affiliation', e.target.value)} className={inputCls} />
                    </div>
                    <div className="md:col-span-2">
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Abstract</label>
                        <textarea id="meta-abstract" rows={4} placeholder="Brief description of your paper's aim, methods, and findings..." value={metadata.abstract || ''} onChange={(e) => setValue('abstract', e.target.value)} className={`${inputCls} resize-none`} />
                    </div>
                    <div>
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Keywords</label>
                        <input id="meta-keywords" type="text" placeholder="e.g. machine learning, NLP, formatting" value={metadata.keywords_raw || ''} onChange={(e) => setValue('keywords_raw', e.target.value)} className={inputCls} />
                    </div>
                    <div>
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Language</label>
                        <select id="meta-language" value={metadata.language || 'english'} onChange={(e) => setValue('language', e.target.value)} className={inputCls}>
                            {['english', 'spanish', 'french', 'german', 'portuguese', 'arabic'].map((l) => (
                                <option key={l} value={l} className="bg-background-light dark:bg-gray-900 text-slate-900 dark:text-slate-100">{l.charAt(0).toUpperCase() + l.slice(1)}</option>
                            ))}
                        </select>
                    </div>
                </div>
                <div>
                    <label className="text-gray-300 text-sm font-medium mb-3 block">Sections to Include</label>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                        {sections.map((section, i) => (
                            <button key={section.name} id={`section-${section.name.toLowerCase().replace(/\s+/g, '-')}`} onClick={() => toggleSection(i)}
                                className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm transition min-h-[44px] ${section.include ? 'border-primary/50 bg-primary/10 text-blue-300' : 'border-white/10 bg-white/5 text-gray-500 hover:text-gray-300'}`}>
                                <span className="material-symbols-outlined text-base">{section.include ? 'check_box' : 'check_box_outline_blank'}</span>
                                {section.name}
                            </button>
                        ))}
                    </div>
                </div>
                <div className="flex items-center gap-3 p-4 rounded-xl bg-white/5 border border-white/10">
                    <input id="option-placeholder" type="checkbox" checked={metadata.include_placeholder !== false} onChange={(e) => setValue('include_placeholder', e.target.checked)} className="w-4 h-4 accent-primary" />
                    <div>
                        <p className="text-slate-900 dark:text-slate-100 text-sm font-medium">Include placeholder content</p>
                        <p className="text-gray-500 text-xs">AI will write full paragraphs for each section (recommended)</p>
                    </div>
                </div>
            </div>
        );
    }

    if (docType === 'resume') {
        const education = metadata.education || [...DEFAULT_RESUME_EDUCATION];
        const experience = metadata.experience || [...DEFAULT_RESUME_EXPERIENCE];
        const resumeInputCls = "bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:border-emerald-500 transition w-full";
        return (
            <div className="space-y-6">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-1">Your Details</h2>
                    <p className="text-slate-500 dark:text-gray-400 text-sm">Fill in your information for the AI to generate your professional CV.</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                        { key: 'name', label: 'Full Name *', placeholder: 'e.g. John Doe', id: 'meta-name' },
                        { key: 'email', label: 'Email', placeholder: 'john@example.com', id: 'meta-email' },
                        { key: 'phone', label: 'Phone', placeholder: '+1 (555) 000-0000', id: 'meta-phone' },
                        { key: 'linkedin', label: 'LinkedIn URL', placeholder: 'linkedin.com/in/johndoe', id: 'meta-linkedin' },
                    ].map((field) => (
                        <div key={field.key}>
                            <label className="text-gray-300 text-sm font-medium mb-1.5 block">{field.label}</label>
                            <input id={field.id} type="text" placeholder={field.placeholder} value={metadata[field.key] || ''} onChange={(e) => setValue(field.key, e.target.value)}
                                className="w-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-3 text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-gray-600 text-sm focus:outline-none focus:border-emerald-500 transition" />
                        </div>
                    ))}
                    <div className="md:col-span-2">
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Professional Summary</label>
                        <textarea id="meta-summary" rows={3} placeholder="Brief professional summary or career objective..." value={metadata.summary || ''} onChange={(e) => setValue('summary', e.target.value)}
                            className="w-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-3 text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-gray-600 text-sm focus:outline-none focus:border-emerald-500 transition resize-none" />
                    </div>
                    <div className="md:col-span-2">
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Skills</label>
                        <input id="meta-skills" type="text" placeholder="e.g. Python, Machine Learning, React" value={metadata.skills_raw || ''} onChange={(e) => setValue('skills_raw', e.target.value)}
                            className="w-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-3 text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-gray-600 text-sm focus:outline-none focus:border-emerald-500 transition" />
                    </div>
                    <div className="md:col-span-2">
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Certifications</label>
                        <input id="meta-certifications" type="text" placeholder="e.g. AWS Certified Developer, PMP" value={metadata.certifications_raw || ''} onChange={(e) => setValue('certifications_raw', e.target.value)}
                            className="w-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-3 text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-gray-600 text-sm focus:outline-none focus:border-emerald-500 transition" />
                    </div>
                </div>
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100">Education</h3>
                        <button type="button" id="btn-add-education" onClick={() => addArrayItem('education', { institution: '', degree: '', year: '' })}
                            className="text-xs px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-white/10 hover:bg-slate-200 dark:hover:bg-white/20 text-slate-700 dark:text-white transition min-h-[36px]">Add Education</button>
                    </div>
                    {education.map((item, i) => (
                        <div key={`education-${i}`} className="grid grid-cols-1 md:grid-cols-3 gap-2 bg-white/5 border border-white/10 rounded-xl p-3">
                            <input type="text" placeholder="Institution" value={item.institution || ''} onChange={(e) => updateArrayItem('education', i, 'institution', e.target.value)} className={resumeInputCls} />
                            <input type="text" placeholder="Degree" value={item.degree || ''} onChange={(e) => updateArrayItem('education', i, 'degree', e.target.value)} className={resumeInputCls} />
                            <div className="flex gap-2">
                                <input type="text" placeholder="Year" value={item.year || ''} onChange={(e) => updateArrayItem('education', i, 'year', e.target.value)} className={`${resumeInputCls} flex-1`} />
                                {education.length > 1 && (
                                    <button type="button" onClick={() => removeArrayItem('education', i)} className="px-2 rounded-lg bg-red-500/20 text-red-300 hover:bg-red-500/30 transition" aria-label="Remove education entry">
                                        <span className="material-symbols-outlined text-base">delete</span>
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100">Experience</h3>
                        <button type="button" id="btn-add-experience" onClick={() => addArrayItem('experience', { company: '', role: '', duration: '', bullets_raw: '' })}
                            className="text-xs px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-white/10 hover:bg-slate-200 dark:hover:bg-white/20 text-slate-700 dark:text-white transition min-h-[36px]">Add Experience</button>
                    </div>
                    {experience.map((item, i) => (
                        <div key={`experience-${i}`} className="grid grid-cols-1 md:grid-cols-2 gap-2 bg-white/5 border border-white/10 rounded-xl p-3">
                            <input type="text" placeholder="Company" value={item.company || ''} onChange={(e) => updateArrayItem('experience', i, 'company', e.target.value)} className={resumeInputCls} />
                            <input type="text" placeholder="Role" value={item.role || ''} onChange={(e) => updateArrayItem('experience', i, 'role', e.target.value)} className={resumeInputCls} />
                            <input type="text" placeholder="Duration (e.g. 2021-2024)" value={item.duration || ''} onChange={(e) => updateArrayItem('experience', i, 'duration', e.target.value)} className={resumeInputCls} />
                            <div className="flex gap-2">
                                <input type="text" placeholder="Bullets (comma separated)" value={item.bullets_raw || ''} onChange={(e) => updateArrayItem('experience', i, 'bullets_raw', e.target.value)} className={`${resumeInputCls} flex-1`} />
                                {experience.length > 1 && (
                                    <button type="button" onClick={() => removeArrayItem('experience', i)} className="px-2 rounded-lg bg-red-500/20 text-red-300 hover:bg-red-500/30 transition" aria-label="Remove experience entry">
                                        <span className="material-symbols-outlined text-base">delete</span>
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-1">Document Details</h2>
                <p className="text-slate-500 dark:text-gray-400 text-sm">Provide details for your {docType.replace('_', ' ')}.</p>
            </div>
            <div className="grid grid-cols-1 gap-4">
                <div>
                    <label className="text-gray-300 text-sm font-medium mb-1.5 block">Title *</label>
                    <input id="meta-title-generic" type="text" placeholder="Document title" value={metadata.title || ''} onChange={(e) => setValue('title', e.target.value)} className={inputCls} />
                </div>
                <div>
                    <label className="text-gray-300 text-sm font-medium mb-1.5 block">Author / Name</label>
                    <input id="meta-name-generic" type="text" placeholder="Your name or organization" value={metadata.name || ''} onChange={(e) => setValue('name', e.target.value)} className={inputCls} />
                </div>
                <div>
                    <label className="text-gray-300 text-sm font-medium mb-1.5 block">Description / Abstract</label>
                    <textarea id="meta-abstract-generic" rows={4} placeholder="Brief description of the document's purpose and content..." value={metadata.abstract || ''} onChange={(e) => setValue('abstract', e.target.value)} className={`${inputCls} resize-none`} />
                </div>
            </div>
        </div>
    );
}

function StepGenerate({ status, progress, stage, message, error, outline, onDownload, onReset }) {
    const stages = [
        { key: 'generating', label: 'Generating content', icon: 'auto_awesome' },
        { key: 'structuring', label: 'Structuring blocks', icon: 'schema' },
        { key: 'formatting', label: 'Applying template', icon: 'format_paint' },
        { key: 'exporting', label: 'Exporting document', icon: 'file_download' },
        { key: 'done', label: 'Document ready', icon: 'check_circle' },
    ];
    const activeIndex = stages.findIndex((item) => item.key === stage);

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-1">
                    {status === 'done' ? 'Document Ready!' : status === 'failed' ? 'Generation Failed' : 'Generating Your Document...'}
                </h2>
                <p className="text-slate-500 dark:text-gray-400 text-sm">{message || 'AI is working on your document...'}</p>
            </div>

            {status !== 'failed' && (
                <div>
                    <div className="flex justify-between text-xs text-gray-500 mb-2">
                        <span>{stage ? stage.charAt(0).toUpperCase() + stage.slice(1) : 'Queued'}</span>
                        <span>{progress}%</span>
                    </div>
                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-blue-500 to-violet-500 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
                    </div>
                </div>
            )}

            <div className="space-y-3">
                {stages.map((item, index) => {
                    const isDone = index < activeIndex || status === 'done';
                    const isActive = item.key === stage && status !== 'done';
                    return (
                        <div key={item.key} className={`flex items-center gap-3 p-3 rounded-xl transition ${isDone ? 'bg-green-500/10' : isActive ? 'bg-primary/10' : 'bg-white/3'}`}>
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isDone ? 'bg-green-500' : isActive ? 'bg-primary' : 'bg-white/10'}`}>
                                <span className="material-symbols-outlined text-white text-sm">{isDone ? 'check' : item.icon}</span>
                            </div>
                            <span className={`text-sm ${isDone ? 'text-green-300' : isActive ? 'text-blue-300' : 'text-gray-600'}`}>{item.label}</span>
                            {isActive && <span className="ml-auto text-xs text-primary-light animate-pulse">In progress...</span>}
                        </div>
                    );
                })}
            </div>

            {outline?.length > 0 && (
                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3">Generated Structure Preview</h3>
                    <ul className="space-y-1.5 text-sm text-gray-300 max-h-56 overflow-y-auto pr-2">
                        {outline.map((item, i) => (
                            <li key={`${item}-${i}`} className="flex gap-2">
                                <span className="text-primary-light">{i + 1}.</span>
                                <span>{item}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {status === 'failed' && error && (
                <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
                    <p className="font-semibold mb-1">Error</p>
                    <p className="font-mono text-xs">{error}</p>
                </div>
            )}

            {status === 'done' && (
                <div className="flex gap-3 flex-wrap">
                    <button id="btn-download-docx" onClick={() => onDownload('docx')}
                        className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary to-primary-hover shadow-lg shadow-primary/30 hover:shadow-primary/50 text-white rounded-xl font-semibold text-sm hover:scale-[1.02] transition active:scale-95">
                        <span className="material-symbols-outlined text-base">file_download</span>
                        Download DOCX
                    </button>
                    <button id="btn-download-pdf" onClick={() => onDownload('pdf')}
                        className="flex items-center gap-2 px-6 py-3 bg-slate-100 dark:bg-white/10 text-slate-800 dark:text-white rounded-xl font-semibold text-sm hover:bg-slate-200 dark:hover:bg-white/20 transition active:scale-95">
                        <span className="material-symbols-outlined text-base">picture_as_pdf</span>
                        Download PDF
                    </button>
                    <button id="btn-generate-another" onClick={onReset}
                        className="flex items-center gap-2 px-6 py-3 bg-slate-100 dark:bg-white/10 text-slate-800 dark:text-white rounded-xl font-semibold text-sm hover:bg-slate-200 dark:hover:bg-white/20 transition active:scale-95">
                        <span className="material-symbols-outlined text-base">add</span>
                        Generate Another
                    </button>
                </div>
            )}

            {status === 'failed' && (
                <button id="btn-try-again" onClick={onReset}
                    className="flex items-center gap-2 px-6 py-3 bg-slate-100 dark:bg-white/10 text-slate-800 dark:text-white rounded-xl font-semibold text-sm hover:bg-slate-200 dark:hover:bg-white/20 transition active:scale-95">
                    <span className="material-symbols-outlined text-base">refresh</span>
                    Try Again
                </button>
            )}
        </div>
    );
}

export default function DocumentGenerator() {
    usePageTitle('Generate Document - ScholarForm AI');
    const { addToast } = useToast();

    const [step, setStep] = useState(1);
    const [docType, setDocType] = useState('');
    const [template, setTemplate] = useState('');
    const [metadata, setMetadata] = useState(makeDefaultMetadata());
    const [jobId, setJobId] = useState(null);
    const [jobStatus, setJobStatus] = useState({ status: 'pending', progress: 0, stage: 'queued', message: '', error: null, outline: [] });
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Warn user about unsaved form data when navigating away mid-form
    const isDirty = step > 1 && step < 4 && (!!docType || !!template);
    useUnsavedChanges(isDirty);

    const streamStopRef = useRef(null);
    const pollingRef = useRef(null);

    const stopBackgroundTracking = useCallback(() => {
        if (typeof streamStopRef.current === 'function') { streamStopRef.current(); streamStopRef.current = null; }
        if (pollingRef.current) { clearInterval(pollingRef.current); pollingRef.current = null; }
    }, []);

    const pullStatusSnapshot = useCallback(async (id) => {
        const snapshot = await getGenerationStatus(id);
        setJobStatus((prev) => ({
            ...prev,
            status: toUiStatus(snapshot.status),
            progress: Number(snapshot.progress || 0),
            stage: String(snapshot.stage || prev.stage || 'queued').toLowerCase(),
            message: snapshot.message || prev.message,
            error: snapshot.error || null,
            outline: Array.isArray(snapshot.outline) ? snapshot.outline : prev.outline,
        }));
    }, []);

    useEffect(() => {
        if (!jobId) return undefined;
        if (jobStatus.status === 'done' || jobStatus.status === 'failed') return undefined;

        let disposed = false;
        stopBackgroundTracking();

        const startPolling = () => {
            if (pollingRef.current) return;
            pollingRef.current = setInterval(async () => {
                try { await pullStatusSnapshot(jobId); } catch { /* swallow */ }
            }, 2000);
        };

        streamGenerationStatus(jobId, ({ event, data }) => {
            if (disposed || event !== 'status_update' || !data || typeof data !== 'object') return;
            const mappedStatus = toUiStatus(data.status);
            setJobStatus((prev) => ({
                ...prev,
                status: mappedStatus,
                progress: typeof data.progress === 'number' ? data.progress : prev.progress,
                stage: String(data.stage || data.phase || prev.stage || 'queued').toLowerCase(),
                message: data.message || prev.message,
                error: data.error || prev.error,
            }));
            if (mappedStatus === 'done' || mappedStatus === 'failed') { void pullStatusSnapshot(jobId); stopBackgroundTracking(); }
        }, () => { if (!disposed) startPolling(); })
            .then((stop) => { if (disposed) stop(); else streamStopRef.current = stop; })
            .catch(() => { if (!disposed) startPolling(); });

        startPolling();
        return () => { disposed = true; stopBackgroundTracking(); };
    }, [jobId, jobStatus.status, pullStatusSnapshot, stopBackgroundTracking]);

    const serializeMetadata = useCallback((raw) => {
        const n = { ...raw };
        if (n.authors_raw) { n.authors = n.authors_raw.split(',').map(v => v.trim()).filter(Boolean); delete n.authors_raw; }
        if (n.keywords_raw) { n.keywords = n.keywords_raw.split(',').map(v => v.trim()).filter(Boolean); delete n.keywords_raw; }
        if (n.skills_raw) { n.skills = n.skills_raw.split(',').map(v => v.trim()).filter(Boolean); delete n.skills_raw; }
        if (n.certifications_raw) { n.certifications = n.certifications_raw.split(',').map(v => v.trim()).filter(Boolean); delete n.certifications_raw; }
        if (Array.isArray(n.experience)) {
            n.experience = n.experience.map(({ bullets_raw, ...rest }) => ({ ...rest, bullets: String(bullets_raw || '').split(',').map(v => v.trim()).filter(Boolean) }));
        }
        return n;
    }, []);

    const handleGenerate = useCallback(async () => {
        setIsSubmitting(true);
        stopBackgroundTracking();
        try {
            const payload = { doc_type: docType, template, metadata: serializeMetadata(metadata), options: { include_placeholder_content: metadata.include_placeholder !== false, word_count_target: 3000 } };
            const response = await generateDocument(payload);
            setJobId(response.job_id);
            setJobStatus({ status: 'pending', progress: 0, stage: 'queued', message: response.message || 'Job queued...', error: null, outline: [] });
            setStep(4);
        } catch (error) {
            addToast(`Failed to start generation: ${error.message}`, 'error');
        } finally {
            setIsSubmitting(false);
        }
    }, [docType, metadata, serializeMetadata, stopBackgroundTracking, template]);

    const handleDownload = useCallback(async (format = 'docx') => {
        if (!jobId) return;
        try {
            const blobUrl = await downloadGeneratedDocument(jobId, format);
            const link = document.createElement('a');
            link.href = blobUrl;
            link.download = `generated_document.${format}`;
            link.click();
        } catch (error) {
            addToast(`Download failed: ${error.message}`, 'error');
        }
    }, [jobId]);

    const handleReset = useCallback(() => {
        stopBackgroundTracking();
        setStep(1); setDocType(''); setTemplate(''); setMetadata(makeDefaultMetadata()); setJobId(null);
        setJobStatus({ status: 'pending', progress: 0, stage: 'queued', message: '', error: null, outline: [] });
    }, [stopBackgroundTracking]);

    useEffect(() => () => stopBackgroundTracking(), [stopBackgroundTracking]);

    const canAdvance = () => {
        if (step === 1) return !!docType;
        if (step === 2) return !!template;
        if (step === 3) {
            if (['academic_paper', 'thesis', 'report', 'portfolio'].includes(docType)) return !!String(metadata.title || '').trim();
            if (docType === 'resume') return !!String(metadata.name || '').trim();
            return true;
        }
        return false;
    };

    const STEPS = [
        { label: 'Document Type', icon: 'category' },
        { label: 'Template', icon: 'style' },
        { label: 'Details', icon: 'edit_note' },
        { label: 'Generate', icon: 'auto_awesome' },
    ];

    return (
        <div className="min-h-screen bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100">
            <div className="max-w-4xl mx-auto px-4 py-10">
                <div className="text-center mb-10">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary-light text-xs font-medium mb-4">
                        <span className="material-symbols-outlined text-sm">auto_awesome</span>
                        AI Document Generator
                    </div>
                    <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-slate-900 to-slate-500 dark:from-white dark:to-gray-400 bg-clip-text text-transparent mb-2">Generate from Scratch</h1>
                    <p className="text-gray-500 text-sm">No file upload needed - describe your document, the AI writes it.</p>
                </div>

                <div className="flex items-center justify-center mb-10">
                    {STEPS.map((stepItem, index) => {
                        const number = index + 1;
                        const isDone = number < step;
                        const isCurrent = number === step;
                        return (
                            <div key={stepItem.label} className="flex items-center">
                                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition ${isDone ? 'text-green-400' : isCurrent ? 'text-primary-light bg-primary/10' : 'text-gray-600'}`}>
                                    <span className="material-symbols-outlined text-sm">{isDone ? 'check_circle' : stepItem.icon}</span>
                                    <span className="hidden sm:inline">{stepItem.label}</span>
                                </div>
                                {index < STEPS.length - 1 && <div className={`w-8 h-px mx-1 ${isDone ? 'bg-green-500/40' : 'bg-slate-300 dark:bg-white/10'}`} />}
                            </div>
                        );
                    })}
                </div>

                <div className="bg-glass-surface backdrop-blur-xl border border-glass-border rounded-2xl p-6 sm:p-8 shadow-2xl shadow-primary/10 animate-in fade-in zoom-in duration-500">
                    {step === 1 && <StepDocType selected={docType} onSelect={(v) => { setDocType(v); setMetadata(makeDefaultMetadata(v)); }} />}
                    {step === 2 && <StepTemplate selected={template} onSelect={setTemplate} />}
                    {step === 3 && <StepMetadata docType={docType} metadata={metadata} onChange={setMetadata} />}
                    {step === 4 && <StepGenerate {...jobStatus} onDownload={handleDownload} onReset={handleReset} />}

                    {step < 4 && (
                        <div className="flex justify-between mt-10 pt-6 border-t border-slate-200 dark:border-white/10">
                            <button id="btn-back" onClick={() => setStep((c) => Math.max(1, c - 1))} disabled={step === 1}
                                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-100 dark:bg-white/5 text-slate-700 dark:text-gray-300 text-sm font-medium hover:bg-slate-200 dark:hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition min-h-[44px]">
                                <span className="material-symbols-outlined text-base">arrow_back</span>
                                Back
                            </button>
                            {step === 3 ? (
                                <button id="btn-generate" onClick={handleGenerate} disabled={!canAdvance() || isSubmitting}
                                    className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-primary to-primary-hover shadow-lg shadow-primary/30 hover:shadow-primary/50 text-white text-sm font-semibold hover:scale-[1.02] disabled:opacity-40 disabled:cursor-not-allowed transition min-h-[44px] active:scale-95">
                                    {isSubmitting ? (
                                        <><span className="material-symbols-outlined text-base animate-spin">progress_activity</span>Starting...</>
                                    ) : (
                                        <><span className="material-symbols-outlined text-base">auto_awesome</span>Generate Document</>
                                    )}
                                </button>
                            ) : (
                                <button id="btn-next" onClick={() => setStep((c) => c + 1)} disabled={!canAdvance()}
                                    className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-primary to-primary-hover shadow-lg shadow-primary/30 hover:shadow-primary/50 text-white text-sm font-semibold hover:scale-[1.02] disabled:opacity-40 disabled:cursor-not-allowed transition min-h-[44px] active:scale-95">
                                    Continue
                                    <span className="material-symbols-outlined text-base">arrow_forward</span>
                                </button>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
