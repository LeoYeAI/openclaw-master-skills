// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
	site: 'https://fernando-fernandez3.github.io',
	base: '/ship-loop',
	integrations: [
		starlight({
			title: 'Ship Loop',
			description: 'Self-healing build pipeline for AI coding agents',
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/fernando-fernandez3/ship-loop' },
			],
			sidebar: [
				{
					label: 'Getting Started',
					items: [
						{ label: 'Introduction', slug: 'getting-started/introduction' },
						{ label: 'Installation', slug: 'getting-started/installation' },
						{ label: 'Quick Start', slug: 'getting-started/quickstart' },
					],
				},
				{
					label: 'Core Concepts',
					items: [
						{ label: 'Architecture', slug: 'concepts/architecture' },
						{ label: 'Learnings Engine', slug: 'concepts/learnings' },
						{ label: 'Budget Tracking', slug: 'concepts/budget' },
					],
				},
				{
					label: 'Reference',
					items: [
						{ label: 'Configuration', slug: 'reference/configuration' },
						{ label: 'CLI Commands', slug: 'reference/cli' },
						{ label: 'Deploy Providers', slug: 'reference/providers' },
					],
				},
				{
					label: 'Guides',
					items: [
						{ label: 'Adding a Provider', slug: 'guides/adding-a-provider' },
						{ label: 'Agent Presets', slug: 'guides/agent-presets' },
					],
				},
			],
			editLink: {
				baseUrl: 'https://github.com/fernando-fernandez3/ship-loop/edit/main/docs/',
			},
			customCss: [],
		}),
	],
});
