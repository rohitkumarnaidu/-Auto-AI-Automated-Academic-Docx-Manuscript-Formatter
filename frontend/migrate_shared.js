import fs from 'fs';
import path from 'path';

const APP_DIR = './app';
const SRC_PAGES = './src/pages';

const sharedRoutes = {
    'Landing.jsx': '(shared)/page.jsx',
    'Login.jsx': '(shared)/login/page.jsx',
    'Signup.jsx': '(shared)/signup/page.jsx',
    'AuthCallback.jsx': '(shared)/auth/callback/page.jsx',
    'ForgotPassword.jsx': '(shared)/forgot-password/page.jsx',
    'VerifyOTP.jsx': '(shared)/verify-otp/page.jsx',
    'ResetPassword.jsx': '(shared)/reset-password/page.jsx',
    'Terms.jsx': '(shared)/terms/page.jsx',
    'Privacy.jsx': '(shared)/privacy/page.jsx',
    'Error.jsx': '(shared)/error/page.jsx' // Note: I already wrote error/page.jsx manually but let's let it overwrite or skip.
};

for (const [srcFile, targetPath] of Object.entries(sharedRoutes)) {
    if (srcFile === 'Error.jsx') continue; // Skipped as I already created it.

    const srcPath = path.join(SRC_PAGES, srcFile);
    const destPath = path.join(APP_DIR, targetPath);

    if (fs.existsSync(srcPath)) {
        // Create directory
        fs.mkdirSync(path.dirname(destPath), { recursive: true });

        let content = fs.readFileSync(srcPath, 'utf8');

        // Add 'use client'
        if (!content.startsWith("'use client'") && !content.startsWith('"use client"')) {
            content = `'use client';\n${content}`;
        }

        // Next.js uses next/link and next/navigation instead of react-router-dom
        // But for this phase, let's just do minimal conversion or leave it to manual fix
        // We will replace react-router-dom imports with next/navigation and next/link where obvious
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

            // Temporary fix for useLocation() -> { pathname: usePathname(), search: useSearchParams().toString() }
            // Let's just keep react-router-dom until Phase 8 or replace it safely where we can

            return result || match;
        });

        fs.writeFileSync(destPath, content);
        console.log(`Ported ${srcFile} to ${targetPath}`);
    } else {
        console.log(`Source file not found: ${srcPath}`);
    }
}
