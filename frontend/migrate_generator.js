import fs from 'fs';
import path from 'path';

const srcPath = './src/pages/DocumentGenerator.jsx';
const destPath = './app/(generator)/(protected)/generate/page.jsx';
fs.mkdirSync(path.dirname(destPath), { recursive: true });
let content = fs.readFileSync(srcPath, 'utf8');

if (!content.startsWith("'use client'") && !content.startsWith('"use client"')) {
    content = `'use client';\n${content}`;
}

content = content.replace(/import\s+{(.*?)}\s+from\s+['"]react-router-dom['"];/g, (match, imports) => {
    const nextImports = [];
    if (imports.includes('useNavigate')) nextImports.push('useRouter as useNavigate');
    if (imports.includes('useLocation')) nextImports.push('usePathname', 'useSearchParams');
    if (imports.includes('useParams')) nextImports.push('useParams');
    return nextImports.length ? `import { ${nextImports.join(', ')} } from 'next/navigation';` : match;
});

fs.writeFileSync(destPath, content);
console.log('Ported Generator');
