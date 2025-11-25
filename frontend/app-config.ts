export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // for LiveKit Cloud Sandbox
  sandboxId?: string;
  agentName?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Teach-the-Tutor',
  pageTitle: 'Teach-the-Tutor: Active Recall Coach',
  pageDescription: 'Master programming concepts through active recall with AI-powered tutors',

  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#6366f1',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#818cf8',
  startButtonText: 'Start Learning',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};
