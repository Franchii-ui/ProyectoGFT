import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  integrations: [react()],
  vite: {
    resolve: {
      alias: {
        '@components': '/src/components',
        '@styles': '/src/styles'
      }
    }
  }
});