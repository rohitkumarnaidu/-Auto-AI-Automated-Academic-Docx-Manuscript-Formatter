import { useState, useEffect, useCallback, useRef } from 'react';
import usePageTitle from '../hooks/usePageTitle';
import {
    downloadGeneratedDocument,
    generateDocument,
    getGenerationStatus,
    streamGenerationStatus,
} from '../services/api';

const DOC_TYPES = [
    {
        id: 'academic_paper',
        label: 'Academic Paper',
        icon: 'article',
        description: 'Research paper with abstract, methodology, results, and references.',
        color: 'from-blue-500 to-blue-700',
    },
    {
        id: 'resume',
        label: 'Resume / CV',
        icon: 'badge',
        description: 'Professional CV with education, experience, and skills sections.',
        color: 'from-emerald-500 to-emerald-700',
    },
    {
        id: 'portfolio',
        label: 'Portfolio',
        icon: 'folder_special',
        description: 'Researcher or creative portfolio with projects and publications.',
        color: 'from-purple-500 to-purple-700',
    },
    {
        id: 'report',
        label: 'Technical Report',
        icon: 'description',
        description: 'Structured technical or business report with findings and recommendations.',
        color: 'from-orange-500 to-orange-700',
    },
    {
        id: 'thesis',
        label: 'Thesis Chapter',
        icon: 'school',
        description: 'Thesis or dissertation chapter with structured academic sections.',
        color: 'from-rose-500 to-rose-700',
    },
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
        return {
            name: '',
            email: '',
            phone: '',
            linkedin: '',
            summary: '',
            skills_raw: '',
            certifications_raw: '',
            education: [...DEFAULT_RESUME_EDUCATION],
            experience: [...DEFAULT_RESUME_EXPERIENCE],
        };
    }

    return {
        sections: [...DEFAULT_PAPER_SECTIONS],
        include_placeholder: true,
        language: 'english',
    };
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
            <h2 className="text-2xl font-bold text-white mb-2">Choose Document Type</h2>
            <p className="text-gray-400 mb-8">Select the type of document you want to generate.</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {DOC_TYPES.map((docType) => (
                    <button
                        key={docType.id}
                        id={`doc-type-${docType.id}`}
                        onClick={() => onSelect(docType.id)}
                        className={`relative group flex flex-col items-start gap-3 p-5 rounded-2xl border-2 transition-all duration-200 text-left ${
                            selected === docType.id
                                ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/20'
                                : 'border-white/10 bg-white/5 hover:border-white/30 hover:bg-white/10'
                        }`}
                    >
                        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${docType.color} flex items-center justify-center`}>
                            <span className="material-symbols-outlined text-white text-xl">{docType.icon}</span>
                        </div>
                        <div>
                            <p className="font-semibold text-white text-sm">{docType.label}</p>
                            <p className="text-gray-400 text-xs mt-1 leading-relaxed">{docType.description}</p>
                        </div>
                        {selected === docType.id && (
                            <span className="absolute top-3 right-3 material-symbols-outlined text-blue-400 text-base">check_circle</span>
                        )}
                    </button>
                ))}
            </div>
        </div>
    );
}

function StepTemplate({ selected, onSelect }) {
    const [filter, setFilter] = useState('');
    const [activeCategory, setActiveCategory] = useState('All');
    const categories = ['All', ...new Set(TEMPLATES.map((template) => template.category))];

    const visibleTemplates = TEMPLATES.filter((template) => {
        const matchesCategory = activeCategory === 'All' || template.category === activeCategory;
        const query = filter.toLowerCase();
        const matchesQuery = template.name.toLowerCase().includes(query) || template.category.toLowerCase().includes(query);
        return matchesCategory && matchesQuery;
    });

    return (
        <div>
            <h2 className="text-2xl font-bold text-white mb-2">Choose a Template</h2>
            <p className="text-gray-400 mb-6">Pick the journal or style template for your document.</p>

            <div className="flex flex-col sm:flex-row gap-3 mb-6">
                <input
                    id="template-search"
                    type="text"
                    placeholder="Search templates..."
                    value={filter}
                    onChange={(event) => setFilter(event.target.value)}
                    className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-blue-500 transition"
                />
                <div className="flex gap-2 flex-wrap">
                    {categories.map((category) => (
                        <button
                            key={category}
                            onClick={() => setActiveCategory(category)}
                            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                                activeCategory === category
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
                            }`}
                        >
                            {category}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {visibleTemplates.map((template) => (
                    <button
                        key={template.id}
                        id={`template-${template.id}`}
                        onClick={() => onSelect(template.id)}
                        className={`flex flex-col items-start gap-1 p-4 rounded-xl border-2 text-left transition-all duration-150 ${
                            selected === template.id
                                ? 'border-blue-500 bg-blue-500/10'
                                : 'border-white/10 bg-white/5 hover:border-white/25 hover:bg-white/8'
                        }`}
                    >
                        <span className={`text-xs font-bold uppercase tracking-wider ${selected === template.id ? 'text-blue-400' : 'text-gray-500'}`}>
                            {template.category}
                        </span>
                        <span className="text-white font-semibold text-sm">{template.name}</span>
                        {selected === template.id && (
                            <span className="material-symbols-outlined text-blue-400 text-sm mt-1">check_circle</span>
                        )}
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

    const addArrayItem = (key, template) => {
        onChange({ ...metadata, [key]: [...(metadata[key] || []), template] });
    };

    const removeArrayItem = (key, index) => {
        const list = [...(metadata[key] || [])];
        list.splice(index, 1);
        onChange({ ...metadata, [key]: list.length ? list : [key === 'education' ? { institution: '', degree: '', year: '' } : { company: '', role: '', duration: '', bullets_raw: '' }] });
    };

    if (docType === 'academic_paper' || docType === 'thesis') {
        const sections = metadata.sections || DEFAULT_PAPER_SECTIONS;
        return (
            <div className="space-y-6">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-1">Document Details</h2>
                    <p className="text-gray-400 text-sm">Fill in the details for your {docType === 'thesis' ? 'thesis chapter' : 'academic paper'}.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Paper Title *</label>
                        <input
                            id="meta-title"
                            type="text"
                            placeholder="e.g. Deep Learning for Academic Document Formatting"
                            value={metadata.title || ''}
                            onChange={(event) => setValue('title', event.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-blue-500 transition"
                        />
                    </div>
                    <div>
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Authors</label>
                        <input
                            id="meta-authors"
                            type="text"
                            placeholder="e.g. John Doe, Jane Smith"
                            value={metadata.authors_raw || ''}
                            onChange={(event) => setValue('authors_raw', event.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-blue-500 transition"
                        />
                    </div>
                    <div>
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Affiliation</label>
                        <input
                            id="meta-affiliation"
                            type="text"
                            placeholder="e.g. MIT, Cambridge University"
                            value={metadata.affiliation || ''}
                            onChange={(event) => setValue('affiliation', event.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-blue-500 transition"
                        />
                    </div>
                    <div className="md:col-span-2">
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Abstract</label>
                        <textarea
                            id="meta-abstract"
                            rows={4}
                            placeholder="Brief description of your paper's aim, methods, and findings..."
                            value={metadata.abstract || ''}
                            onChange={(event) => setValue('abstract', event.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-blue-500 transition resize-none"
                        />
                    </div>
                    <div>
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Keywords</label>
                        <input
                            id="meta-keywords"
                            type="text"
                            placeholder="e.g. machine learning, NLP, formatting"
                            value={metadata.keywords_raw || ''}
                            onChange={(event) => setValue('keywords_raw', event.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-blue-500 transition"
                        />
                    </div>
                    <div>
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Language</label>
                        <select
                            id="meta-language"
                            value={metadata.language || 'english'}
                            onChange={(event) => setValue('language', event.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-blue-500 transition"
                        >
                            {['english', 'spanish', 'french', 'german', 'portuguese', 'arabic'].map((language) => (
                                <option key={language} value={language} className="bg-gray-900">
                                    {language.charAt(0).toUpperCase() + language.slice(1)}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div>
                    <label className="text-gray-300 text-sm font-medium mb-3 block">Sections to Include</label>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                        {sections.map((section, index) => (
                            <button
                                key={section.name}
                                id={`section-${section.name.toLowerCase().replace(/\s+/g, '-')}`}
                                onClick={() => toggleSection(index)}
                                className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm transition ${
                                    section.include
                                        ? 'border-blue-500/50 bg-blue-500/10 text-blue-300'
                                        : 'border-white/10 bg-white/5 text-gray-500 hover:text-gray-300'
                                }`}
                            >
                                <span className="material-symbols-outlined text-base">
                                    {section.include ? 'check_box' : 'check_box_outline_blank'}
                                </span>
                                {section.name}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="flex items-center gap-3 p-4 rounded-xl bg-white/5 border border-white/10">
                    <input
                        id="option-placeholder"
                        type="checkbox"
                        checked={metadata.include_placeholder !== false}
                        onChange={(event) => setValue('include_placeholder', event.target.checked)}
                        className="w-4 h-4 accent-blue-500"
                    />
                    <div>
                        <p className="text-white text-sm font-medium">Include placeholder content</p>
                        <p className="text-gray-500 text-xs">AI will write full paragraphs for each section (recommended)</p>
                    </div>
                </div>
            </div>
        );
    }

    if (docType === 'resume') {
        const education = metadata.education || [...DEFAULT_RESUME_EDUCATION];
        const experience = metadata.experience || [...DEFAULT_RESUME_EXPERIENCE];
        return (
            <div className="space-y-6">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-1">Your Details</h2>
                    <p className="text-gray-400 text-sm">Fill in your information for the AI to generate your professional CV.</p>
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
                            <input
                                id={field.id}
                                type="text"
                                placeholder={field.placeholder}
                                value={metadata[field.key] || ''}
                                onChange={(event) => setValue(field.key, event.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-emerald-500 transition"
                            />
                        </div>
                    ))}
                    <div className="md:col-span-2">
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Professional Summary</label>
                        <textarea
                            id="meta-summary"
                            rows={3}
                            placeholder="Brief professional summary or career objective..."
                            value={metadata.summary || ''}
                            onChange={(event) => setValue('summary', event.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-emerald-500 transition resize-none"
                        />
                    </div>
                    <div className="md:col-span-2">
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Skills</label>
                        <input
                            id="meta-skills"
                            type="text"
                            placeholder="e.g. Python, Machine Learning, React"
                            value={metadata.skills_raw || ''}
                            onChange={(event) => setValue('skills_raw', event.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-emerald-500 transition"
                        />
                    </div>
                    <div className="md:col-span-2">
                        <label className="text-gray-300 text-sm font-medium mb-1.5 block">Certifications</label>
                        <input
                            id="meta-certifications"
                            type="text"
                            placeholder="e.g. AWS Certified Developer, PMP"
                            value={metadata.certifications_raw || ''}
                            onChange={(event) => setValue('certifications_raw', event.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-emerald-500 transition"
                        />
                    </div>
                </div>

                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <h3 className="text-base font-semibold text-white">Education</h3>
                        <button
                            type="button"
                            id="btn-add-education"
                            onClick={() => addArrayItem('education', { institution: '', degree: '', year: '' })}
                            className="text-xs px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white"
                        >
                            Add Education
                        </button>
                    </div>
                    {education.map((item, index) => (
                        <div key={`education-${index}`} className="grid grid-cols-1 md:grid-cols-3 gap-2 bg-white/5 border border-white/10 rounded-xl p-3">
                            <input
                                type="text"
                                placeholder="Institution"
                                value={item.institution || ''}
                                onChange={(event) => updateArrayItem('education', index, 'institution', event.target.value)}
                                className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                            />
                            <input
                                type="text"
                                placeholder="Degree"
                                value={item.degree || ''}
                                onChange={(event) => updateArrayItem('education', index, 'degree', event.target.value)}
                                className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                            />
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    placeholder="Year"
                                    value={item.year || ''}
                                    onChange={(event) => updateArrayItem('education', index, 'year', event.target.value)}
                                    className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                                />
                                {education.length > 1 && (
                                    <button
                                        type="button"
                                        onClick={() => removeArrayItem('education', index)}
                                        className="px-2 rounded-lg bg-red-500/20 text-red-300 hover:bg-red-500/30"
                                    >
                                        <span className="material-symbols-outlined text-base">delete</span>
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <h3 className="text-base font-semibold text-white">Experience</h3>
                        <button
                            type="button"
                            id="btn-add-experience"
                            onClick={() => addArrayItem('experience', { company: '', role: '', duration: '', bullets_raw: '' })}
                            className="text-xs px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white"
                        >
                            Add Experience
                        </button>
                    </div>
                    {experience.map((item, index) => (
                        <div key={`experience-${index}`} className="grid grid-cols-1 md:grid-cols-2 gap-2 bg-white/5 border border-white/10 rounded-xl p-3">
                            <input
                                type="text"
                                placeholder="Company"
                                value={item.company || ''}
                                onChange={(event) => updateArrayItem('experience', index, 'company', event.target.value)}
                                className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                            />
                            <input
                                type="text"
                                placeholder="Role"
                                value={item.role || ''}
                                onChange={(event) => updateArrayItem('experience', index, 'role', event.target.value)}
                                className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                            />
                            <input
                                type="text"
                                placeholder="Duration (e.g. 2021-2024)"
                                value={item.duration || ''}
                                onChange={(event) => updateArrayItem('experience', index, 'duration', event.target.value)}
                                className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                            />
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    placeholder="Bullets (comma separated)"
                                    value={item.bullets_raw || ''}
                                    onChange={(event) => updateArrayItem('experience', index, 'bullets_raw', event.target.value)}
                                    className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                                />
                                {experience.length > 1 && (
                                    <button
                                        type="button"
                                        onClick={() => removeArrayItem('experience', index)}
                                        className="px-2 rounded-lg bg-red-500/20 text-red-300 hover:bg-red-500/30"
                                    >
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
                <h2 className="text-2xl font-bold text-white mb-1">Document Details</h2>
                <p className="text-gray-400 text-sm">Provide details for your {docType.replace('_', ' ')}.</p>
            </div>
            <div className="grid grid-cols-1 gap-4">
                <div>
                    <label className="text-gray-300 text-sm font-medium mb-1.5 block">Title *</label>
                    <input
                        id="meta-title-generic"
                        type="text"
                        placeholder="Document title"
                        value={metadata.title || ''}
                        onChange={(event) => setValue('title', event.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-blue-500 transition"
                    />
                </div>
                <div>
                    <label className="text-gray-300 text-sm font-medium mb-1.5 block">Author / Name</label>
                    <input
                        id="meta-name-generic"
                        type="text"
                        placeholder="Your name or organization"
                        value={metadata.name || ''}
                        onChange={(event) => setValue('name', event.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-blue-500 transition"
                    />
                </div>
                <div>
                    <label className="text-gray-300 text-sm font-medium mb-1.5 block">Description / Abstract</label>
                    <textarea
                        id="meta-abstract-generic"
                        rows={4}
                        placeholder="Brief description of the document's purpose and content..."
                        value={metadata.abstract || ''}
                        onChange={(event) => setValue('abstract', event.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-blue-500 transition resize-none"
                    />
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
                <h2 className="text-2xl font-bold text-white mb-1">
                    {status === 'done' ? 'Document Ready!' : status === 'failed' ? 'Generation Failed' : 'Generating Your Document...'}
                </h2>
                <p className="text-gray-400 text-sm">{message || 'AI is working on your document...'}</p>
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
                        <div
                            key={item.key}
                            className={`flex items-center gap-3 p-3 rounded-xl transition ${isDone ? 'bg-green-500/10' : isActive ? 'bg-blue-500/10' : 'bg-white/3'}`}
                        >
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isDone ? 'bg-green-500' : isActive ? 'bg-blue-500' : 'bg-white/10'}`}>
                                <span className="material-symbols-outlined text-white text-sm">{isDone ? 'check' : item.icon}</span>
                            </div>
                            <span className={`text-sm ${isDone ? 'text-green-300' : isActive ? 'text-blue-300' : 'text-gray-600'}`}>{item.label}</span>
                            {isActive && <span className="ml-auto text-xs text-blue-400 animate-pulse">In progress...</span>}
                        </div>
                    );
                })}
            </div>

            {outline?.length > 0 && (
                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                    <h3 className="text-sm font-semibold text-white mb-3">Generated Structure Preview</h3>
                    <ul className="space-y-1.5 text-sm text-gray-300 max-h-56 overflow-y-auto pr-2">
                        {outline.map((item, index) => (
                            <li key={`${item}-${index}`} className="flex gap-2">
                                <span className="text-blue-400">{index + 1}.</span>
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
                    <button
                        id="btn-download-docx"
                        onClick={() => onDownload('docx')}
                        className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-violet-600 text-white rounded-xl font-semibold text-sm hover:from-blue-700 hover:to-violet-700 transition"
                    >
                        <span className="material-symbols-outlined text-base">file_download</span>
                        Download DOCX
                    </button>
                    <button
                        id="btn-download-pdf"
                        onClick={() => onDownload('pdf')}
                        className="flex items-center gap-2 px-6 py-3 bg-white/10 text-white rounded-xl font-semibold text-sm hover:bg-white/20 transition"
                    >
                        <span className="material-symbols-outlined text-base">picture_as_pdf</span>
                        Download PDF
                    </button>
                    <button
                        id="btn-generate-another"
                        onClick={onReset}
                        className="flex items-center gap-2 px-6 py-3 bg-white/10 text-white rounded-xl font-semibold text-sm hover:bg-white/20 transition"
                    >
                        <span className="material-symbols-outlined text-base">add</span>
                        Generate Another
                    </button>
                </div>
            )}

            {status === 'failed' && (
                <button
                    id="btn-try-again"
                    onClick={onReset}
                    className="flex items-center gap-2 px-6 py-3 bg-white/10 text-white rounded-xl font-semibold text-sm hover:bg-white/20 transition"
                >
                    <span className="material-symbols-outlined text-base">refresh</span>
                    Try Again
                </button>
            )}
        </div>
    );
}

export default function DocumentGenerator() {
    usePageTitle('Generate Document - ScholarForm AI');

    const [step, setStep] = useState(1);
    const [docType, setDocType] = useState('');
    const [template, setTemplate] = useState('');
    const [metadata, setMetadata] = useState(makeDefaultMetadata());
    const [jobId, setJobId] = useState(null);
    const [jobStatus, setJobStatus] = useState({
        status: 'pending',
        progress: 0,
        stage: 'queued',
        message: '',
        error: null,
        outline: [],
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const streamStopRef = useRef(null);
    const pollingRef = useRef(null);

    const stopBackgroundTracking = useCallback(() => {
        if (typeof streamStopRef.current === 'function') {
            streamStopRef.current();
            streamStopRef.current = null;
        }
        if (pollingRef.current) {
            clearInterval(pollingRef.current);
            pollingRef.current = null;
        }
    }, []);

    const pullStatusSnapshot = useCallback(async (id) => {
        const snapshot = await getGenerationStatus(id);
        setJobStatus((previous) => ({
            ...previous,
            status: toUiStatus(snapshot.status),
            progress: Number(snapshot.progress || 0),
            stage: String(snapshot.stage || previous.stage || 'queued').toLowerCase(),
            message: snapshot.message || previous.message,
            error: snapshot.error || null,
            outline: Array.isArray(snapshot.outline) ? snapshot.outline : previous.outline,
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
                try {
                    await pullStatusSnapshot(jobId);
                } catch {
                    // swallow polling hiccups
                }
            }, 2000);
        };

        streamGenerationStatus(
            jobId,
            ({ event, data }) => {
                if (disposed) return;
                if (event !== 'status_update' || !data || typeof data !== 'object') return;

                const incoming = data;
                const mappedStatus = toUiStatus(incoming.status);
                setJobStatus((previous) => ({
                    ...previous,
                    status: mappedStatus,
                    progress: typeof incoming.progress === 'number' ? incoming.progress : previous.progress,
                    stage: String(incoming.stage || incoming.phase || previous.stage || 'queued').toLowerCase(),
                    message: incoming.message || previous.message,
                    error: incoming.error || previous.error,
                }));

                if (mappedStatus === 'done' || mappedStatus === 'failed') {
                    void pullStatusSnapshot(jobId);
                    stopBackgroundTracking();
                }
            },
            () => {
                if (!disposed) startPolling();
            }
        )
            .then((stopStream) => {
                if (disposed) {
                    stopStream();
                    return;
                }
                streamStopRef.current = stopStream;
            })
            .catch(() => {
                if (!disposed) startPolling();
            });

        startPolling();

        return () => {
            disposed = true;
            stopBackgroundTracking();
        };
    }, [jobId, jobStatus.status, pullStatusSnapshot, stopBackgroundTracking]);

    const serializeMetadata = useCallback((rawMetadata) => {
        const normalized = { ...rawMetadata };

        if (normalized.authors_raw) {
            normalized.authors = normalized.authors_raw.split(',').map((value) => value.trim()).filter(Boolean);
            delete normalized.authors_raw;
        }
        if (normalized.keywords_raw) {
            normalized.keywords = normalized.keywords_raw.split(',').map((value) => value.trim()).filter(Boolean);
            delete normalized.keywords_raw;
        }
        if (normalized.skills_raw) {
            normalized.skills = normalized.skills_raw.split(',').map((value) => value.trim()).filter(Boolean);
            delete normalized.skills_raw;
        }
        if (normalized.certifications_raw) {
            normalized.certifications = normalized.certifications_raw.split(',').map((value) => value.trim()).filter(Boolean);
            delete normalized.certifications_raw;
        }

        if (Array.isArray(normalized.experience)) {
            normalized.experience = normalized.experience.map((item) => ({
                ...item,
                bullets: String(item.bullets_raw || '')
                    .split(',')
                    .map((value) => value.trim())
                    .filter(Boolean),
            }));
            normalized.experience = normalized.experience.map(({ bullets_raw, ...rest }) => rest);
        }

        return normalized;
    }, []);

    const handleGenerate = useCallback(async () => {
        setIsSubmitting(true);
        stopBackgroundTracking();

        try {
            const payload = {
                doc_type: docType,
                template,
                metadata: serializeMetadata(metadata),
                options: {
                    include_placeholder_content: metadata.include_placeholder !== false,
                    word_count_target: 3000,
                },
            };

            const response = await generateDocument(payload);
            setJobId(response.job_id);
            setJobStatus({
                status: 'pending',
                progress: 0,
                stage: 'queued',
                message: response.message || 'Job queued...',
                error: null,
                outline: [],
            });
            setStep(4);
        } catch (error) {
            alert(`Failed to start generation: ${error.message}`);
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
            alert(`Download failed: ${error.message}`);
        }
    }, [jobId]);

    const handleReset = useCallback(() => {
        stopBackgroundTracking();
        setStep(1);
        setDocType('');
        setTemplate('');
        setMetadata(makeDefaultMetadata());
        setJobId(null);
        setJobStatus({
            status: 'pending',
            progress: 0,
            stage: 'queued',
            message: '',
            error: null,
            outline: [],
        });
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
        <div className="min-h-screen bg-gray-950 text-white">
            <div className="max-w-4xl mx-auto px-4 py-10">
                <div className="text-center mb-10">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium mb-4">
                        <span className="material-symbols-outlined text-sm">auto_awesome</span>
                        AI Document Generator
                    </div>
                    <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent mb-2">
                        Generate from Scratch
                    </h1>
                    <p className="text-gray-500 text-sm">No file upload needed - describe your document, the AI writes it.</p>
                </div>

                <div className="flex items-center justify-center mb-10">
                    {STEPS.map((stepItem, index) => {
                        const number = index + 1;
                        const isDone = number < step;
                        const isCurrent = number === step;
                        return (
                            <div key={stepItem.label} className="flex items-center">
                                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition ${isDone ? 'text-green-400' : isCurrent ? 'text-blue-400 bg-blue-500/10' : 'text-gray-600'}`}>
                                    <span className="material-symbols-outlined text-sm">{isDone ? 'check_circle' : stepItem.icon}</span>
                                    <span className="hidden sm:inline">{stepItem.label}</span>
                                </div>
                                {index < STEPS.length - 1 && (
                                    <div className={`w-8 h-px mx-1 ${isDone ? 'bg-green-500/40' : 'bg-white/10'}`} />
                                )}
                            </div>
                        );
                    })}
                </div>

                <div className="bg-white/5 border border-white/10 rounded-2xl p-6 sm:p-8">
                    {step === 1 && (
                        <StepDocType
                            selected={docType}
                            onSelect={(value) => {
                                setDocType(value);
                                setMetadata(makeDefaultMetadata(value));
                            }}
                        />
                    )}
                    {step === 2 && <StepTemplate selected={template} onSelect={setTemplate} />}
                    {step === 3 && <StepMetadata docType={docType} metadata={metadata} onChange={setMetadata} />}
                    {step === 4 && (
                        <StepGenerate
                            {...jobStatus}
                            onDownload={handleDownload}
                            onReset={handleReset}
                        />
                    )}

                    {step < 4 && (
                        <div className="flex justify-between mt-10 pt-6 border-t border-white/10">
                            <button
                                id="btn-back"
                                onClick={() => setStep((current) => Math.max(1, current - 1))}
                                disabled={step === 1}
                                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white/5 text-gray-300 text-sm font-medium hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition"
                            >
                                <span className="material-symbols-outlined text-base">arrow_back</span>
                                Back
                            </button>

                            {step === 3 ? (
                                <button
                                    id="btn-generate"
                                    onClick={handleGenerate}
                                    disabled={!canAdvance() || isSubmitting}
                                    className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white text-sm font-semibold hover:from-blue-700 hover:to-violet-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
                                >
                                    {isSubmitting ? (
                                        <>
                                            <span className="material-symbols-outlined text-base animate-spin">progress_activity</span>
                                            Starting...
                                        </>
                                    ) : (
                                        <>
                                            <span className="material-symbols-outlined text-base">auto_awesome</span>
                                            Generate Document
                                        </>
                                    )}
                                </button>
                            ) : (
                                <button
                                    id="btn-next"
                                    onClick={() => setStep((current) => current + 1)}
                                    disabled={!canAdvance()}
                                    className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white text-sm font-semibold hover:from-blue-700 hover:to-violet-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
                                >
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
