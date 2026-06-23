import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'evnar',
  tagline: 'APM-pakke med agent-skills — installer, last inn, bruk',
  favicon: 'img/favicon.svg',

  // GitHub Pages: https://mmsge.github.io/evnar/
  url: 'https://mmsge.github.io',
  baseUrl: '/evnar/',
  organizationName: 'mmsge',
  projectName: 'evnar',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',

  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  // All prose is Norwegian Nynorsk.
  i18n: {
    defaultLocale: 'nn',
    locales: ['nn'],
  },

  // Read by the boot-screen home page (src/pages/index.tsx).
  customFields: {
    skillCount: 11,
    version: '0.1.0',
  },

  presets: [
    [
      'classic',
      {
        docs: {
          path: 'docs',
          routeBasePath: 'docs',
          sidebarPath: './sidebars.ts',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: true,
      respectPrefersColorScheme: false,
    },
    navbar: {
      title: 'EVNAR.DOC',
      items: [
        {to: '/docs/intro', label: '[F1] HANDBOK', position: 'left'},
        {to: '/docs/installering/apm', label: '[F2] INSTALLER', position: 'left'},
        {to: '/docs/skills/oversikt', label: '[F3] SKILLS', position: 'left'},
        {
          href: 'https://github.com/mmsge/evnar',
          label: 'GITHUB',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'HANDBOK',
          items: [
            {label: 'Introduksjon', to: '/docs/intro'},
            {label: 'Installering — APM', to: '/docs/installering/apm'},
            {label: 'Last ned og last inn', to: '/docs/installering/manuell'},
            {label: 'Alle skills', to: '/docs/skills/oversikt'},
          ],
        },
        {
          title: 'APM',
          items: [
            {label: 'APM-kjeldeformatet', to: '/docs/apm-format'},
            {
              label: 'Agent Package Manager ↗',
              href: 'https://microsoft.github.io/apm/',
            },
          ],
        },
        {
          title: 'KJELDE',
          items: [{label: 'mmsge/evnar ↗', href: 'https://github.com/mmsge/evnar'}],
        },
      ],
      copyright:
        'EVNAR.DOC · © 2026 MARKUS · bygd med APM + Docusaurus · [PgDn] FOR MEIR',
    },
    prism: {
      theme: prismThemes.vsDark,
      darkTheme: prismThemes.vsDark,
      additionalLanguages: ['bash', 'yaml', 'json', 'python', 'toml'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
