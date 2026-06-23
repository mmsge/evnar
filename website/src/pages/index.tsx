import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './index.module.css';

type Fields = {
  skillCount?: number;
  version?: string;
  evnarUrl?: string;
  isPrivate?: boolean;
};

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  const cf = (siteConfig.customFields ?? {}) as Fields;
  const skills = cf.skillCount ?? 0;
  const version = cf.version ?? '0.1.0';
  const banner = (siteConfig.title ?? 'EVNAR').toUpperCase();

  return (
    <Layout title="BIOS" description={siteConfig.tagline}>
      <main className={styles.boot}>
        <pre className={styles.screen}>
          {`==================================================\n`}
          {`  `}
          <span className={styles.title}>{`${banner} BIOS  v${version}`}</span>
          {`\n`}
          {`  (C) 2026 MARKUS - APM SKILLS PACKAGE\n`}
          {`==================================================\n\n`}
          {`  POST .......................... `}
          <span className={styles.ok}>OK</span>
          {`\n`}
          {`  Minne ......................... `}
          <span className={styles.ok}>640K OK</span>
          {`\n`}
          {`  Agent-klientar ................ claude cursor codex gemini ...\n`}
          {`  Skannar .apm/skills ........... `}
          <span className={styles.ok}>{`${skills} SKILLS FUNNE`}</span>
          {`\n`}
          {`  Monterer APM-kjeldetre ........ `}
          <span className={styles.ok}>OK</span>
          {`\n`}
          {cf.evnarUrl ? (
            <>
              {`  Avhengnad mmsge/evnar ......... `}
              <a className={styles.depLink} href={cf.evnarUrl}>
                [LENKA]
              </a>
              {`\n`}
            </>
          ) : null}
          {cf.isPrivate ? (
            <span className={styles.warn}>
              {`\n  [!] PRIVAT PAKKE - personlege skills, ikkje for offentleg deling\n`}
            </span>
          ) : null}
          {`\n  > Klar. Trykk `}
          <span className={styles.ok}>[ENTER]</span>
          {` for aa opne handboka `}
          <span className="dos-cursor" />
        </pre>

        <div className={styles.actions}>
          <Link className="button button--primary button--lg" to="/docs/intro">
            &raquo; OPN HANDBOKA
          </Link>
          <Link className="button button--lg" to="/docs/installering/apm">
            &raquo; INSTALLER
          </Link>
          {cf.evnarUrl ? (
            <a className="button button--lg" href={cf.evnarUrl}>
              evnar &#8599;
            </a>
          ) : null}
        </div>
      </main>
    </Layout>
  );
}
