import fs from 'fs';
import path from 'path';

const APP_DIR = './app';
const SRC_PAGES = './src/pages';

const formatterRoutes = {
    'Upload.jsx': '(formatter)/upload/page.jsx',
    'Processing.jsx': '(formatter)/processing/page.jsx',
    'ValidationResults.jsx': '(formatter)/results/page.jsx',
    'Download.jsx': '(formatter)/download/page.jsx',
    'Compare.jsx': '(formatter)/compare/page.jsx',
    'Preview.jsx': '(formatter)/preview/page.jsx',
    'Edit.jsx': '(formatter)/edit/page.jsx',
    'Templates.jsx': '(formatter)/templates/page.jsx',
    // Protected roots
    'History.jsx': '(formatter)/(protected)/history/page.jsx',
    'TemplateEditor.jsx': '(formatter)/(protected)/template-editor/page.jsx',
    'BatchUpload.jsx': '(formatter)/(protected)/batch-upload/page.jsx',
};

for (const [srcFile, targetPath] of Object.entries(formatterRoutes)) {
    const srcPath = path.join(SRC_PAGES, srcFile);
    const destPath = path.join(APP_DIR, targetPath);

    if (fs.existsSync(srcPath)) {
        fs.mkdirSync(path.dirname(destPath), { recursive: true });

        let content = fs.readFileSync(srcPath, 'utf8');

        if (!content.startsWith("'use client'") && !content.startsWith('"use client"')) {
            content = `'use client';\n${content}`;
        }

        content = content.replace(/import\s+{(.*?)}\s+from\s+['"]react-router-dom['"];/g, (match, imports) => {
            const nextImports = [];
            const nextLinkImports = [];

            if (imports.includes('useNavigate')) nextImports.push('useRouter as useNavigate');
            if (imports.includes('useLocation')) nextImports.push('usePathname', 'useSearchParams');
            if (imports.includes('useParams')) nextImports.push('useParams');
            if (imports.includes('Link')) nextLinkImports.push('Link');
            if (imports.includes('Navigate')) nextImports.push('redirect');

            let result = '';
            if (nextImports.length > 0) result += `import { ${nextImports.join(', ')} } from 'next/navigation';\n`;
            if (nextLinkImports.length > 0) result += `import Link from 'next/link';\n`;

            return result || match;
        });

        fs.writeFileSync(destPath, content);
        console.log(`Ported ${srcFile} to ${targetPath}`);
    } else {
        console.log(`Source file not found: ${srcPath}`);
    }
}
