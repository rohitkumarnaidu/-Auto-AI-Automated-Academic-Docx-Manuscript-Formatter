/* eslint-env node */
module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/upload',
        'http://localhost:3000/live',
        'http://localhost:3000/agent',
        'http://localhost:3000/dashboard',
        'http://localhost:3000/history'
      ],
      startServerCommand: 'npm run start',
    },
    upload: {
      target: 'temporary-public-storage',
    },
    assert: {
      preset: 'lighthouse:no-pwa',
      assertions: {
        'categories:performance': ['warn', { minScore: 0.8 }],
        'categories:accessibility': ['warn', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
        'categories:seo': ['warn', { minScore: 0.9 }],
      }
    }
  },
};
