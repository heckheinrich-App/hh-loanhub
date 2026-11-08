import os

html_content = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>HH Cash Solutions — Your Financial Partner</title>

  <!-- PWA Meta Tags & Strict Cache Control -->
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <link rel="manifest" href="/manifest.json?v=6">
  <meta name="theme-color" content="#0B7A28">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="HH Cash">
  <link rel="apple-touch-icon" href="/icons/icon-192.png?v=6">
  <link rel="icon" type="image/svg+xml" href="/icons/icon.svg?v=6">
  <link rel="icon" type="image/png" href="/icons/icon-192.png?v=6">

  <style>
    /* --------------------------------------------------------------------------
       DESIGN SYSTEM & CSS VARIABLES
       Matching HH Cash Solutions Official Design Board
       -------------------------------------------------------------------------- */
    :root {
      --primary-green: #0B7A28;
      --primary-green-light: #19A93E;
      --primary-green-dark: #08561C;
      --green-gradient: linear-gradient(135deg, #0B7A28 0%, #19A93E 100%);
      --green-subtle: #E8F5E9;
      --accent-gold: #F59E0B;
      --accent-gold-light: #FCD34D;
      --bg-canvas: #F0F2F5;
      --bg-surface: #FFFFFF;
      --bg-card: #FFFFFF;
      --text-main: #111827;
      --text-muted: #6B7280;
      --text-light: #9CA3AF;
      --border-subtle: #E5E7EB;
      --border-focus: #0B7A28;
      --status-red: #EF4444;
      --status-amber: #F59E0B;
      --status-blue: #2563EB;
      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 20px;
      --radius-full: 9999px;
      --shadow-soft: 0 4px 20px -2px rgba(0, 0, 0, 0.06), 0 2px 6px -1px rgba(0, 0, 0, 0.04);
      --shadow-green: 0 8px 24px -4px rgba(11, 122, 40, 0.35);
      --shadow-elevated: 0 12px 32px -4px rgba(0, 0, 0, 0.12);
      --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-tap-highlight-color: transparent;
    }

    body {
      background-color: var(--bg-canvas);
      color: var(--text-main);
      font-family: var(--font-family);
      min-height: 100dvh;
      margin: 0;
      padding: 0;
      line-height: 1.45;
      overflow-x: hidden;
      display: flex;
      justify-content: center;
      align-items: stretch;
    }

    /* TRUE RESPONSIVE FULL-SCREEN APP CONTAINER (No Fake Bezels) */
    .app-viewport {
      width: 100%;
      min-height: 100dvh;
      background: var(--bg-surface);
      display: flex;
      flex-direction: column;
      position: relative;
      margin: 0;
      box-shadow: none !important;
      border: none !important;
      border-radius: 0 !important;
    }

    /* Master Admin Sticky Switcher Bar */
    .admin-bar {
      position: sticky;
      top: 0;
      width: 100%;
      background: #111827;
      color: #FFF;
      padding: 10px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      z-index: 1050;
      box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }
    .admin-toggle-btn {
      background: #0B7A28;
      color: #FFF;
      border: none;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 800;
      cursor: pointer;
      transition: background 0.15s ease;
    }
    .admin-toggle-btn:hover {
      background: #19A93E;
    }

    /* View Content Container */
    .view-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      position: relative;
      width: 100%;
      padding-bottom: 90px;
    }

    /* Common View Class */
    .view-screen {
      display: none;
      flex-direction: column;
      width: 100%;
      max-width: 760px;
      margin: 0 auto;
      padding: 24px 20px 40px 20px;
      animation: fadeIn 0.25s ease-out;
    }
    .view-screen.active {
      display: flex;
    }
    @media (min-width: 768px) {
      .view-screen {
        padding: 36px 24px 60px 24px;
      }
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* --------------------------------------------------------------------------
       SPLASH SCREEN
       -------------------------------------------------------------------------- */
    .splash-container {
      position: fixed;
      inset: 0;
      background: #FFFFFF;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      align-items: center;
      padding: 60px 24px 40px 24px;
      transition: opacity 0.35s ease;
    }
    .splash-center {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      flex: 1;
      width: 100%;
      max-width: 320px;
    }
    .splash-illustration {
      width: 220px;
      height: 200px;
      margin-bottom: 24px;
      filter: drop-shadow(0 14px 24px rgba(11, 122, 40, 0.18));
      animation: gentleFloat 3s ease-in-out infinite;
    }
    @keyframes gentleFloat {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-8px); }
    }
    .splash-pills-row {
      display: flex;
      gap: 12px;
      margin-top: 10px;
    }
    .splash-pill-dot {
      font-size: 13px;
      font-weight: 700;
      color: #374151;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .splash-pill-dot::after {
      content: "•";
      color: #9CA3AF;
      margin-left: 6px;
    }
    .splash-pill-dot:last-child::after {
      content: "";
    }

    /* --------------------------------------------------------------------------
       BRANDING & LOGO HEADERS
       -------------------------------------------------------------------------- */
    .brand-header {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 20px;
      padding-top: 8px;
    }
    .brand-logo-svg {
      width: 200px;
      height: 80px;
      overflow: visible;
    }
    .brand-tagline {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      letter-spacing: 0.05em;
      margin-top: 4px;
    }

    /* --------------------------------------------------------------------------
       FORM CONTROLS & INPUTS
       -------------------------------------------------------------------------- */
    .login-heading {
      text-align: center;
      margin-bottom: 24px;
    }
    .login-heading h2 {
      font-size: 24px;
      font-weight: 800;
      color: var(--text-main);
      margin-bottom: 4px;
    }
    .login-heading p {
      font-size: 14px;
      color: var(--text-muted);
    }
    .form-group {
      margin-bottom: 16px;
      width: 100%;
    }
    .form-label {
      display: block;
      font-size: 13px;
      font-weight: 700;
      color: #374151;
      margin-bottom: 6px;
    }
    .input-wrapper {
      position: relative;
      display: flex;
      align-items: center;
      width: 100%;
    }
    .input-icon {
      position: absolute;
      left: 16px;
      width: 20px;
      height: 20px;
      color: #9CA3AF;
      pointer-events: none;
    }
    .input-pill {
      width: 100%;
      height: 52px;
      padding: 0 48px 0 48px;
      background: #FFFFFF;
      border: 1.5px solid var(--border-subtle);
      border-radius: var(--radius-full);
      font-size: 15px;
      font-family: inherit;
      color: var(--text-main);
      transition: all 0.2s ease;
      outline: none;
    }
    .input-pill:focus {
      border-color: var(--border-focus);
      box-shadow: 0 0 0 3px rgba(11, 122, 40, 0.15);
    }
    .input-toggle-eye {
      position: absolute;
      right: 16px;
      width: 20px;
      height: 20px;
      color: #9CA3AF;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* Password Strength Meter */
    .pwd-meter-box {
      margin-top: 6px;
      width: 100%;
    }
    .pwd-meter-bar {
      width: 100%;
      height: 5px;
      background: #E5E7EB;
      border-radius: 3px;
      overflow: hidden;
      margin-top: 4px;
    }
    .pwd-meter-fill {
      height: 100%;
      width: 0%;
      border-radius: 3px;
      transition: width 0.3s ease, background-color 0.3s ease;
    }
    .pwd-helper-text {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 4px;
      display: flex;
      justify-content: space-between;
    }

    /* --------------------------------------------------------------------------
       BUTTONS
       -------------------------------------------------------------------------- */
    .btn-green {
      width: 100%;
      height: 52px;
      background: var(--green-gradient);
      color: #FFFFFF;
      border: none;
      border-radius: var(--radius-full);
      font-size: 16px;
      font-weight: 700;
      font-family: inherit;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: var(--shadow-green);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .btn-green:active {
      transform: scale(0.98);
      box-shadow: 0 4px 12px rgba(11, 122, 40, 0.25);
    }
    .btn-green:disabled {
      opacity: 0.65;
      cursor: not-allowed;
      transform: none;
    }

    .btn-biometric {
      width: 100%;
      height: 50px;
      background: #FFFFFF;
      color: var(--primary-green-dark);
      border: 2px solid var(--primary-green);
      border-radius: var(--radius-full);
      font-size: 15px;
      font-weight: 800;
      font-family: inherit;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      margin-top: 12px;
      box-shadow: 0 2px 8px rgba(11, 122, 40, 0.1);
      transition: all 0.2s ease;
    }
    .btn-biometric:hover {
      background: var(--green-subtle);
    }
    .btn-biometric:active {
      transform: scale(0.98);
    }

    .btn-white-outlined {
      width: 100%;
      height: 52px;
      background: #FFFFFF;
      color: var(--primary-green);
      border: 2px solid var(--primary-green);
      border-radius: var(--radius-full);
      font-size: 15px;
      font-weight: 700;
      font-family: inherit;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: background 0.15s ease;
    }
    .btn-white-outlined:hover {
      background: #F0FDF4;
    }

    .link-forgot {
      display: block;
      text-align: center;
      font-size: 13px;
      color: var(--text-muted);
      text-decoration: none;
      margin-top: 14px;
      font-weight: 600;
      cursor: pointer;
    }
    .divider-or {
      display: flex;
      align-items: center;
      text-align: center;
      margin: 18px 0;
      color: #9CA3AF;
      font-size: 13px;
      font-weight: 600;
    }
    .divider-or::before, .divider-or::after {
      content: '';
      flex: 1;
      border-bottom: 1px solid #E5E7EB;
    }
    .divider-or span {
      padding: 0 12px;
    }

    .cursive-footer {
      font-family: "Brush Script MT", "Caveat", "Segoe Script", cursive, sans-serif;
      font-size: 22px;
      color: #08561C;
      text-align: center;
      margin-top: 28px;
      opacity: 0.95;
    }

    /* --------------------------------------------------------------------------
       KYC FILE UPLOAD BOXES
       -------------------------------------------------------------------------- */
    .kyc-upload-group {
      margin-bottom: 14px;
    }
    .kyc-box {
      border: 1.5px dashed #CBD5E1;
      border-radius: var(--radius-md);
      padding: 14px;
      background: #F8FAFC;
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      position: relative;
    }
    .kyc-box:hover, .kyc-box.has-file {
      border-color: var(--primary-green);
      background: #F0FDF4;
    }
    .kyc-icon-badge {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: #E2E8F0;
      color: #475569;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .kyc-box.has-file .kyc-icon-badge {
      background: #DCFCE7;
      color: var(--primary-green);
    }
    .kyc-info {
      flex: 1;
      min-width: 0;
    }
    .kyc-title {
      font-size: 13px;
      font-weight: 700;
      color: #1E293B;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .kyc-desc {
      font-size: 11px;
      color: var(--text-muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .kyc-input-hidden {
      display: none;
    }
    .kyc-check-icon {
      color: var(--primary-green);
      display: none;
      flex-shrink: 0;
    }
    .kyc-box.has-file .kyc-check-icon {
      display: block;
    }

    /* --------------------------------------------------------------------------
       LOAN SLIDER & 30% BREAKDOWN CARD
       -------------------------------------------------------------------------- */
    .loan-slider-container {
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: var(--radius-lg);
      padding: 18px;
      margin-bottom: 16px;
    }
    .loan-amount-display {
      font-size: 32px;
      font-weight: 900;
      color: var(--primary-green-dark);
      text-align: center;
      margin: 8px 0;
      letter-spacing: -0.5px;
    }
    .range-slider-pill {
      -webkit-appearance: none;
      width: 100%;
      height: 8px;
      border-radius: 4px;
      background: #E2E8F0;
      outline: none;
      margin: 12px 0;
    }
    .range-slider-pill::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: var(--primary-green);
      cursor: pointer;
      box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    .slider-labels {
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
    }

    .breakdown-card {
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: var(--radius-md);
      padding: 14px;
      margin-top: 10px;
    }
    .breakdown-row {
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      padding: 4px 0;
      color: #4B5563;
    }
    .breakdown-row.total-row {
      border-top: 1.5px dashed #E2E8F0;
      margin-top: 6px;
      padding-top: 8px;
      font-weight: 800;
      font-size: 15px;
      color: var(--primary-green-dark);
    }

    /* --------------------------------------------------------------------------
       CLIENT DASHBOARD HERO & LIFECYCLE BANNERS
       -------------------------------------------------------------------------- */
    .home-top-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }
    .top-logo-compact {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .top-logo-text {
      font-size: 18px;
      font-weight: 900;
      color: var(--primary-green-dark);
      line-height: 1.1;
    }
    .top-logo-sub {
      font-size: 11px;
      color: var(--text-muted);
      font-weight: 600;
    }
    .top-action-icons {
      display: flex;
      gap: 8px;
    }
    .top-icon-btn {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: #F3F4F6;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #374151;
      cursor: pointer;
      position: relative;
    }
    .notif-badge-dot {
      position: absolute;
      top: 8px;
      right: 8px;
      width: 8px;
      height: 8px;
      background: #EF4444;
      border-radius: 50%;
      border: 1.5px solid #FFF;
    }

    /* Lifecycle Status Banner Card */
    .lifecycle-banner {
      width: 100%;
      border-radius: var(--radius-lg);
      padding: 16px;
      margin-bottom: 16px;
      display: none;
      animation: fadeIn 0.25s ease-out;
    }
    .lifecycle-banner.pending {
      background: #FFFBEB;
      border: 1.5px solid #FCD34D;
      color: #92400E;
    }
    .lifecycle-banner.approved {
      background: #EFF6FF;
      border: 1.5px solid #93C5FD;
      color: #1E40AF;
    }
    .lifecycle-banner.active-loan {
      background: #F0FDF4;
      border: 1.5px solid #86EFAC;
      color: #065F46;
    }
    .lifecycle-banner.payment-requested {
      background: #FEF2F2;
      border: 2px solid #F87171;
      color: #991B1B;
      box-shadow: 0 4px 14px rgba(239, 68, 68, 0.15);
    }

    /* Hero Balance Card */
    .hero-balance-card {
      background: var(--green-gradient);
      border-radius: var(--radius-lg);
      padding: 24px;
      color: #FFFFFF;
      box-shadow: var(--shadow-green);
      margin-bottom: 24px;
      position: relative;
      overflow: hidden;
    }
    .hero-top-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 16px;
    }
    .hero-label {
      font-size: 13px;
      font-weight: 600;
      opacity: 0.9;
    }
    .hero-amount {
      font-size: 34px;
      font-weight: 900;
      letter-spacing: -0.5px;
      margin-top: 2px;
    }
    .wallet-icon-badge {
      width: 48px;
      height: 48px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(8px);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #FFF;
    }
    .hero-account-badge {
      display: inline-block;
      background: rgba(255, 255, 255, 0.2);
      padding: 5px 12px;
      border-radius: var(--radius-full);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.03em;
    }

    /* 2x2 Action Grid */
    .action-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
      margin-bottom: 24px;
    }
    .action-card {
      background: #FFFFFF;
      border-radius: var(--radius-lg);
      padding: 20px 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      box-shadow: var(--shadow-soft);
      cursor: pointer;
      border: 1px solid #F3F4F6;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .action-card:active {
      transform: scale(0.97);
    }
    .action-icon-disc {
      width: 54px;
      height: 54px;
      border-radius: 50%;
      background: var(--green-subtle);
      color: var(--primary-green);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 12px;
    }
    .action-title {
      font-size: 14px;
      font-weight: 700;
      color: var(--text-main);
      line-height: 1.25;
    }

    /* Promo Banner */
    .promo-banner {
      background: linear-gradient(135deg, #064E1C 0%, #0B7A28 100%);
      border-radius: var(--radius-lg);
      padding: 20px;
      color: #FFFFFF;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: var(--shadow-green);
      position: relative;
      overflow: hidden;
    }
    .promo-content {
      max-width: 60%;
      z-index: 2;
    }
    .promo-content h4 {
      font-size: 15px;
      font-weight: 800;
      line-height: 1.3;
      margin-bottom: 10px;
    }
    .btn-promo-apply {
      background: #FFFFFF;
      color: var(--primary-green-dark);
      border: none;
      padding: 8px 18px;
      border-radius: var(--radius-full);
      font-size: 13px;
      font-weight: 800;
      cursor: pointer;
    }
    .promo-graphic {
      width: 100px;
      height: 80px;
      z-index: 1;
    }

    /* --------------------------------------------------------------------------
       ADMIN COMMAND CENTER
       -------------------------------------------------------------------------- */
    .admin-stats-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      margin-bottom: 20px;
    }
    @media (min-width: 600px) {
      .admin-stats-grid {
        grid-template-columns: repeat(3, 1fr);
      }
    }
    .admin-stat-card {
      background: #FFFFFF;
      border: 1px solid #E5E7EB;
      border-radius: var(--radius-md);
      padding: 14px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .admin-stat-val {
      font-size: 20px;
      font-weight: 900;
      color: var(--primary-green-dark);
    }
    .admin-stat-lbl {
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      margin-top: 2px;
    }

    .admin-tabs {
      display: flex;
      gap: 6px;
      margin-bottom: 16px;
      overflow-x: auto;
      padding-bottom: 4px;
    }
    .admin-tab-btn {
      padding: 8px 14px;
      border-radius: var(--radius-full);
      font-size: 12px;
      font-weight: 700;
      border: 1px solid #E5E7EB;
      background: #FFFFFF;
      color: #4B5563;
      cursor: pointer;
      white-space: nowrap;
    }
    .admin-tab-btn.active {
      background: var(--primary-green);
      color: #FFFFFF;
      border-color: var(--primary-green);
    }

    /* Admin Cards */
    .admin-queue-card {
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: var(--radius-lg);
      padding: 18px;
      margin-bottom: 16px;
      box-shadow: var(--shadow-soft);
    }
    .admin-queue-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 8px;
    }
    .admin-badge {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
    }
    .badge-pending { background: #FEF3C7; color: #92400E; }
    .badge-approved { background: #DBEAFE; color: #1E40AF; }
    .badge-active { background: #DCFCE7; color: #166534; }
    .badge-payment_requested { background: #FEE2E2; color: #991B1B; }

    .ocr-report-box {
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: var(--radius-md);
      padding: 12px;
      margin: 12px 0;
    }
    .ocr-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      font-size: 12px;
      font-weight: 800;
    }
    .ocr-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 6px;
      font-size: 12px;
    }

    .doc-pills-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin: 10px 0;
    }
    .doc-pill-btn {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 5px 10px;
      background: #EFF6FF;
      color: #1E40AF;
      border: 1px solid #BFDBFE;
      border-radius: var(--radius-sm);
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      text-decoration: none;
    }
    .doc-pill-btn:hover {
      background: #DBEAFE;
    }

    .admin-action-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
      padding-top: 12px;
      border-top: 1px solid #F1F5F9;
    }
    .btn-adm {
      padding: 8px 14px;
      border-radius: var(--radius-sm);
      font-size: 12px;
      font-weight: 800;
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .btn-adm-approve { background: #10B981; color: #FFF; }
    .btn-adm-decline { background: #EF4444; color: #FFF; }
    .btn-adm-payout { background: #0B7A28; color: #FFF; }
    .btn-adm-pull { background: #F59E0B; color: #FFF; }
    .btn-adm-whatsapp { background: #25D366; color: #FFF; }
    .btn-adm-secondary { background: #E2E8F0; color: #334155; }

    /* --------------------------------------------------------------------------
       BOTTOM NAVIGATION DOCK
       -------------------------------------------------------------------------- */
    .bottom-nav {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      background: #FFFFFF;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      justify-content: center;
      z-index: 1000;
      padding-bottom: env(safe-area-inset-bottom, 0);
    }
    .bottom-nav-inner {
      width: 100%;
      max-width: 600px;
      height: 64px;
      display: flex;
      justify-content: space-around;
      align-items: center;
    }
    .nav-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 4px;
      color: #9CA3AF;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      flex: 1;
      height: 100%;
    }
    .nav-item.active {
      color: var(--primary-green);
    }
    .nav-item svg {
      width: 22px;
      height: 22px;
    }

    /* --------------------------------------------------------------------------
       MODALS & DIALOGS
       -------------------------------------------------------------------------- */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(4px);
      z-index: 2000;
      display: none;
      align-items: flex-end;
      justify-content: center;
    }
    .modal-overlay.active {
      display: flex;
    }
    .modal-sheet {
      width: 100%;
      max-width: 600px;
      background: #FFFFFF;
      border-radius: 26px 26px 0 0;
      padding: 24px 20px 32px 20px;
      box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.2);
      animation: slideUp 0.25s ease-out;
      max-height: 88vh;
      overflow-y: auto;
    }
    @media (min-width: 768px) {
      .modal-overlay {
        align-items: center;
        padding: 20px;
      }
      .modal-sheet {
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
        animation: fadeIn 0.2s ease-out;
      }
      .sheet-handle {
        display: none;
      }
    }
    @keyframes slideUp {
      from { transform: translateY(100%); }
      to { transform: translateY(0); }
    }
    .sheet-handle {
      width: 40px;
      height: 4px;
      background: #E5E7EB;
      border-radius: 2px;
      margin: 0 auto 16px auto;
    }
    .sheet-title {
      font-size: 18px;
      font-weight: 800;
      margin-bottom: 12px;
    }

    .toast-msg {
      position: fixed;
      top: 24px;
      left: 50%;
      transform: translateX(-50%);
      width: calc(100% - 32px);
      max-width: 480px;
      background: #111827;
      color: #FFF;
      padding: 13px 18px;
      border-radius: var(--radius-md);
      font-size: 13px;
      font-weight: 600;
      display: none;
      align-items: center;
      gap: 10px;
      z-index: 99999;
      box-shadow: var(--shadow-elevated);
    }
    .toast-msg.show {
      display: flex;
      animation: fadeIn 0.2s ease-out;
    }

    /* User Profile Card */
    .profile-card {
      background: #FFFFFF;
      border-radius: var(--radius-lg);
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      box-shadow: var(--shadow-soft);
      margin-bottom: 20px;
    }
    .profile-avatar-disc {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: var(--green-subtle);
      color: var(--primary-green-dark);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      font-weight: 900;
    }
    .profile-info h3 {
      font-size: 18px;
      font-weight: 800;
      color: var(--text-main);
    }
    .profile-info p {
      font-size: 13px;
      color: var(--text-muted);
      font-weight: 600;
    }

    .menu-list {
      background: #FFFFFF;
      border-radius: var(--radius-lg);
      overflow: hidden;
      box-shadow: var(--shadow-soft);
      margin-bottom: 24px;
    }
    .menu-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 18px;
      border-bottom: 1px solid #F3F4F6;
      cursor: pointer;
      font-size: 14px;
      font-weight: 700;
      color: #1F2937;
    }
    .menu-item:last-child {
      border-bottom: none;
    }
    .menu-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .menu-item-icon {
      color: var(--primary-green);
      display: flex;
    }
    .chevron-icon {
      color: #9CA3AF;
    }
  </style>
</head>
<body>

  <div class="app-viewport">

    <!-- Master Admin Role Switcher Bar (Appears when Admin logs in) -->
    <div id="adminTopBar" class="admin-bar" style="display: none;">
      <span>👑 Admin Mode: Hein</span>
      <button class="admin-toggle-btn" id="btnAdminToggleView" onclick="toggleAdminView()">
        Switch to Admin Center
      </button>
    </div>

    <!-- Toast Notification Popup -->
    <div id="toastBox" class="toast-msg">
      <span id="toastIcon">ℹ️</span>
      <span id="toastText">Message</span>
    </div>

    <!-- MAIN SCROLLABLE VIEW CONTAINER -->
    <div class="view-container">

      <!-- ====================================================================
           SPLASH SCREEN (2.2-Second Brand Intro)
           ==================================================================== -->
      <div id="splashScreen" class="splash-container">
        <div></div>
        <div class="splash-center">
          <svg class="splash-illustration" viewBox="0 0 240 220" fill="none" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="120" cy="195" rx="90" ry="14" fill="#000000" opacity="0.08"/>
            <path d="M 65 190 C 50 135, 60 95, 100 80 C 105 78, 110 65, 120 65 C 130 65, 135 78, 140 80 C 180 95, 190 135, 175 190 Z" fill="#D4AF37"/>
            <path d="M 100 80 Q 120 90 140 80 Q 120 72 100 80 Z" fill="#B8860B"/>
            <text x="120" y="155" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="900" font-size="52" fill="#78350F" text-anchor="middle">R</text>
            <rect x="25" y="155" width="40" height="12" rx="4" fill="#EAB308"/>
            <rect x="25" y="140" width="40" height="12" rx="4" fill="#FACC15"/>
            <rect x="25" y="125" width="40" height="12" rx="4" fill="#FDE047"/>
          </svg>
          <div style="font-size: 26px; font-weight: 900; color: #08561C; text-align: center; line-height: 1.1;">
            HH Cash Solutions
          </div>
          <div style="font-size: 13px; font-weight: 700; color: #0B7A28; margin-top: 4px;">
            — Your Financial Partner —
          </div>
          <div class="splash-pills-row">
            <span class="splash-pill-dot">Quick</span>
            <span class="splash-pill-dot">Easy</span>
            <span class="splash-pill-dot">Reliable</span>
          </div>
        </div>
        <div class="cursive-footer">Together Towards Financial Freedom</div>
      </div>


      <!-- ====================================================================
           LOGIN SCREEN
           ==================================================================== -->
      <div id="loginScreen" class="view-screen">
        <div class="brand-header">
          <svg class="brand-logo-svg" viewBox="0 0 280 110" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M 40 52 C 85 8, 175 8, 245 36 C 185 22, 100 22, 52 58 Z" fill="#0B7A28"/>
            <path d="M 60 48 C 100 16, 170 16, 235 40 C 180 28, 115 28, 72 52 Z" fill="#19A93E"/>
            <text x="140" y="68" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="900" font-style="italic" font-size="54" fill="#0B7A28" text-anchor="middle" letter-spacing="-2">HH</text>
            <text x="140" y="100" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="900" font-size="28" fill="#08561C" text-anchor="middle" letter-spacing="-0.5">Cash Solutions</text>
          </svg>
          <div class="brand-tagline">— Your Financial Partner —</div>
        </div>

        <div class="login-heading">
          <h2>Welcome Back</h2>
          <p>Login to manage your loans</p>
        </div>

        <!-- PWA Install Banner -->
        <div class="install-banner" id="pwaInstallBanner" style="display: none; background: #F0FDF4; border: 1px solid #86EFAC; border-radius: 12px; padding: 12px; margin-bottom: 16px; align-items: center; justify-content: space-between;">
          <div style="font-size: 13px; font-weight: 700; color: #166534;">📲 Install HH Cash on your phone</div>
          <button style="background: #0B7A28; color: #FFF; border: none; padding: 6px 12px; border-radius: 6px; font-weight: 800; font-size: 12px; cursor: pointer;" onclick="triggerPwaInstall()">Install</button>
        </div>

        <!-- Login Form -->
        <form onsubmit="handleLoginSubmit(event)">
          <div class="form-group">
            <div class="input-wrapper">
              <svg class="input-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              <input type="text" class="input-pill" id="loginPhone" placeholder="Phone Number or Username (e.g. 0821234567 or Hein)" required>
            </div>
          </div>

          <div class="form-group">
            <div class="input-wrapper">
              <svg class="input-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 11V7a5 5 0 0110 0v4"/>
              </svg>
              <input type="password" class="input-pill" id="loginPassword" placeholder="Password" required>
              <span class="input-toggle-eye" onclick="togglePasswordVisibility('loginPassword', this)">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
              </span>
            </div>
          </div>

          <button type="submit" class="btn-green" id="btnLogin">
            Login
          </button>
        </form>

        <!-- Biometric Sign-In Button -->
        <button type="button" class="btn-biometric" id="btnBiometricLogin" onclick="triggerBiometricLogin()">
          <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 004 11m0 0a8.003 8.003 0 0115.357-2m1.519 4.884A15.938 15.938 0 0020 11"/>
          </svg>
          Sign in with Biometrics (Fingerprint / Face ID)
        </button>

        <!-- Fast Master Admin Preset Shortcut -->
        <div style="text-align: center; margin-top: 14px;">
          <button type="button" style="background: none; border: none; font-size: 12px; font-weight: 700; color: #4B5563; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;" onclick="fillMasterAdminLogin()">
            🔒 Master Admin Portal (Hein)
          </button>
        </div>

        <a class="link-forgot" onclick="openForgotPasswordModal()">Forgot Password?</a>

        <div class="divider-or">
          <span>or</span>
        </div>

        <button type="button" class="btn-white-outlined" onclick="navigateToScreen('registerScreen')">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
          </svg>
          Register New Account
        </button>

        <div class="cursive-footer">Together Towards Financial Freedom</div>
      </div>


      <!-- ====================================================================
           REGISTRATION SCREEN (KYC Uploads + OCR Affordability + 30% Loan Request)
           ==================================================================== -->
      <div id="registerScreen" class="view-screen">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
          <button style="background: none; border: none; cursor: pointer; color: #111827; display: flex;" onclick="navigateToScreen('loginScreen')">
            <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          <div style="font-size: 20px; font-weight: 800;">New Borrower Registration</div>
        </div>

        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 20px;">
          Complete registration with your KYC documents. Our OCR Affordability Engine instantly calculates your max loan capacity!
        </p>

        <form id="regForm" onsubmit="handleRegisterWithKycSubmit(event)">
          <!-- Personal Info -->
          <div class="form-group">
            <label class="form-label">Full Legal Name</label>
            <input type="text" class="input-pill" style="padding-left: 20px;" id="regFullName" placeholder="e.g. John Peter Smith" required>
          </div>

          <div class="form-group">
            <label class="form-label">Phone Number (Username)</label>
            <input type="tel" class="input-pill" style="padding-left: 20px;" id="regPhone" placeholder="e.g. 0821234567" required>
          </div>

          <div class="form-group">
            <label class="form-label">SA ID Number / Passport</label>
            <input type="text" class="input-pill" style="padding-left: 20px;" id="regIdNumber" placeholder="13-digit SA ID number" required>
          </div>

          <div class="form-group">
            <label class="form-label">Residential Address</label>
            <input type="text" class="input-pill" style="padding-left: 20px;" id="regAddress" placeholder="Physical street address & postal code" required>
          </div>

          <!-- Bank Account Details for EFT Payout -->
          <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: var(--radius-md); padding: 14px; margin-bottom: 16px;">
            <div style="font-size: 13px; font-weight: 800; color: #1E293B; margin-bottom: 10px;">
              🏦 Banking Details (For EFT Loan Payout)
            </div>
            <div class="form-group">
              <label class="form-label">Bank Name</label>
              <input type="text" class="input-pill" style="padding-left: 20px;" id="regBankName" placeholder="e.g. Capitec, FNB, Standard Bank, Nedbank, Absa" required>
            </div>
            <div class="form-group" style="margin-bottom: 0;">
              <label class="form-label">Account Number</label>
              <input type="text" class="input-pill" style="padding-left: 20px;" id="regBankAccountNumber" placeholder="e.g. 1234567890" required>
            </div>
          </div>

          <!-- Password with Live Strength Indicator & Friendly Policy -->
          <div class="form-group">
            <label class="form-label">Create Password</label>
            <div class="input-wrapper">
              <input type="password" class="input-pill" style="padding-left: 20px;" id="regPassword" placeholder="Create a strong password (4 to 20+ characters)" oninput="updatePasswordStrength(this.value)" required>
              <span class="input-toggle-eye" onclick="togglePasswordVisibility('regPassword', this)">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
              </span>
            </div>
            <div class="pwd-meter-box">
              <div class="pwd-meter-bar">
                <div class="pwd-meter-fill" id="pwdMeterFill"></div>
              </div>
              <div class="pwd-helper-text">
                <span>Use as many characters as you like (at least 4 characters required)</span>
                <strong id="pwdStrengthLabel" style="color: #6B7280;">Too short</strong>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Confirm Password</label>
            <input type="password" class="input-pill" style="padding-left: 20px;" id="regConfirmPassword" placeholder="Re-type password" required>
          </div>

          <!-- Initial Loan Request Selector (30% Interest) -->
          <div class="loan-slider-container">
            <div style="font-size: 14px; font-weight: 800; color: #1E293B; margin-bottom: 4px;">
              Select Initial Loan Amount
            </div>
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">
              Fixed 30% Interest Rate &bull; Due on Month-End Deduction Date
            </div>
            <div class="loan-amount-display" id="regLoanAmountText">R5 000.00</div>
            <input type="range" class="range-slider-pill" id="regLoanSlider" min="500" max="20000" step="500" value="5000" oninput="updateRegLoanCalculation(this.value)">
            <div class="slider-labels">
              <span>Min: R500</span>
              <span>Max: R20 000</span>
            </div>

            <div class="breakdown-card">
              <div class="breakdown-row">
                <span>Principal Borrowed:</span>
                <strong id="regBreakdownPrincipal">R5 000.00</strong>
              </div>
              <div class="breakdown-row">
                <span>30% Fixed Interest:</span>
                <strong id="regBreakdownInterest" style="color: var(--primary-green);">+ R1 500.00</strong>
              </div>
              <div class="breakdown-row total-row">
                <span>Total Repayable:</span>
                <strong id="regBreakdownTotal">R6 500.00</strong>
              </div>
            </div>
          </div>

          <!-- KYC Document Upload Dropzones -->
          <div style="margin-bottom: 20px;">
            <div style="font-size: 14px; font-weight: 800; color: #1E293B; margin-bottom: 4px;">
              📑 Required KYC Documents
            </div>
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">
              Upload clear PDF files or photos (max 10MB each). Analyzed locally by OCR.
            </div>

            <!-- 1. 3-Month Bank Statement -->
            <div class="kyc-upload-group">
              <div class="kyc-box" id="boxBankStatement" onclick="document.getElementById('fileBankStatement').click()">
                <div class="kyc-icon-badge">📄</div>
                <div class="kyc-info">
                  <div class="kyc-title">3-Month Bank Statement <span style="color: #EF4444;">*</span></div>
                  <div class="kyc-desc" id="descBankStatement">PDF or photo from your banking app</div>
                </div>
                <div class="kyc-check-icon">✓ Selected</div>
              </div>
              <input type="file" id="fileBankStatement" class="kyc-input-hidden" accept=".pdf,image/*" onchange="onKycFilePicked('BankStatement', this)" required>
            </div>

            <!-- 2. Copy of ID Document -->
            <div class="kyc-upload-group">
              <div class="kyc-box" id="boxIdDocument" onclick="document.getElementById('fileIdDocument').click()">
                <div class="kyc-icon-badge">🪪</div>
                <div class="kyc-info">
                  <div class="kyc-title">Copy of SA ID / Passport <span style="color: #EF4444;">*</span></div>
                  <div class="kyc-desc" id="descIdDocument">Smart ID card (both sides), green book, or passport</div>
                </div>
                <div class="kyc-check-icon">✓ Selected</div>
              </div>
              <input type="file" id="fileIdDocument" class="kyc-input-hidden" accept=".pdf,image/*" onchange="onKycFilePicked('IdDocument', this)" required>
            </div>

            <!-- 3. Proof of Residence -->
            <div class="kyc-upload-group">
              <div class="kyc-box" id="boxProofResidence" onclick="document.getElementById('fileProofResidence').click()">
                <div class="kyc-icon-badge">🏠</div>
                <div class="kyc-info">
                  <div class="kyc-title">Proof of Residential Address <span style="color: #EF4444;">*</span></div>
                  <div class="kyc-desc" id="descProofResidence">Utility bill, store account, or rental agreement (&lt;3 months)</div>
                </div>
                <div class="kyc-check-icon">✓ Selected</div>
              </div>
              <input type="file" id="fileProofResidence" class="kyc-input-hidden" accept=".pdf,image/*" onchange="onKycFilePicked('ProofResidence', this)" required>
            </div>
          </div>

          <!-- Submit Button -->
          <button type="submit" class="btn-green" id="btnSubmitRegister">
            Submit Application & Create Account
          </button>
        </form>

        <div style="height: 40px;"></div>
      </div>


      <!-- ====================================================================
           CLIENT HOME DASHBOARD
           ==================================================================== -->
      <div id="homeScreen" class="view-screen">
        <div class="home-top-bar">
          <div class="top-logo-compact">
            <svg width="40" height="34" viewBox="0 0 120 90" fill="none" style="overflow: visible; flex-shrink: 0;">
              <path d="M12 46 C 42 10, 85 10, 114 32 C 85 20, 48 20, 20 50 Z" fill="#0B7A28"/>
              <path d="M24 42 C 48 16, 80 16, 108 34 C 82 25, 52 25, 30 46 Z" fill="#19A93E"/>
              <text x="60" y="74" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="900" font-style="italic" font-size="44" fill="#0B7A28" text-anchor="middle" letter-spacing="-1">HH</text>
            </svg>
            <div style="display: flex; flex-direction: column;">
              <span class="top-logo-text">HH Cash Solutions</span>
              <span class="top-logo-sub">Your Financial Partner</span>
            </div>
          </div>
          <div class="top-action-icons">
            <button class="top-icon-btn" onclick="openShareAppModal()" title="Share App">
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
                <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
              </svg>
            </button>
            <button class="top-icon-btn" onclick="openNotificationsModal()" title="Notifications">
              <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
              </svg>
              <div id="homeNotifDot" class="notif-badge-dot" style="display: none;"></div>
            </button>
          </div>
        </div>

        <!-- Dynamic Loan Lifecycle Banner -->
        <div id="lifecycleBanner" class="lifecycle-banner">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
            <strong id="lifecycleTitle" style="font-size: 14px;">Loan Status Update</strong>
            <span id="lifecycleBadge" class="admin-badge">Status</span>
          </div>
          <p id="lifecycleMessage" style="font-size: 13px; line-height: 1.4; margin-bottom: 10px;"></p>
          <div id="lifecycleActionContainer" style="display: none;"></div>
        </div>

        <!-- Green Hero Balance Card -->
        <div class="hero-balance-card">
          <div class="hero-top-row">
            <div>
              <div class="hero-label">Available Balance</div>
              <div class="hero-amount" id="homeBalanceDisplay">R12 500.00</div>
            </div>
            <div class="wallet-icon-badge">
              <svg width="26" height="26" fill="currentColor" viewBox="0 0 24 24">
                <path d="M21 7.28V5c0-1.1-.9-2-2-2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-2.28c.59-.35 1-.98 1-1.72V9c0-.74-.41-1.37-1-1.72zM20 9v6h-7V9h7zM5 19V5h14v2h-6c-1.1 0-2 .9-2 2v6c0 1.1.9 2 2 2h6v2H5z"/>
                <circle cx="16" cy="12" r="1.5"/>
              </svg>
            </div>
          </div>
          <div class="hero-account-badge" id="homeAccountBadge">Account Number: #123456</div>
        </div>

        <!-- 2x2 Action Grid -->
        <div class="action-grid">
          <div class="action-card" onclick="startLoanWizard()">
            <div class="action-icon-disc">
              <svg width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <div class="action-title">Apply<br>for a Loan</div>
          </div>

          <div class="action-card" onclick="navigateToScreen('repaymentsScreen')">
            <div class="action-icon-disc">
              <svg width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
            </div>
            <div class="action-title">My<br>Repayments</div>
          </div>

          <div class="action-card" onclick="navigateToScreen('myLoansScreen')">
            <div class="action-icon-disc">
              <svg width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/>
                <line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>
              </svg>
            </div>
            <div class="action-title">My<br>Loans</div>
          </div>

          <div class="action-card" onclick="openSupportModal()">
            <div class="action-icon-disc">
              <svg width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 100-6 3 3 0 000 6z"/>
              </svg>
            </div>
            <div class="action-title">Support<br>& Contact</div>
          </div>
        </div>

        <!-- Promo Banner -->
        <div class="promo-banner">
          <div class="promo-content">
            <h4>Need a little extra? Apply for a loan today!</h4>
            <button class="btn-promo-apply" onclick="startLoanWizard()">Apply Now</button>
          </div>
          <div class="promo-graphic">
            <svg viewBox="0 0 90 80" width="100%" height="100%">
              <rect x="10" y="25" width="60" height="35" rx="3" fill="#D97706" transform="rotate(-15 10 25)"/>
              <rect x="18" y="20" width="60" height="35" rx="3" fill="#059669" transform="rotate(-5 18 20)"/>
              <rect x="25" y="15" width="60" height="35" rx="3" fill="#2563EB" transform="rotate(8 25 15)"/>
              <circle cx="58" cy="36" r="8" fill="#FCD34D" opacity="0.9"/>
              <text x="58" y="39" font-size="7" font-weight="900" fill="#111827" text-anchor="middle">R200</text>
            </svg>
          </div>
        </div>
      </div>


      <!-- ====================================================================
           APPLY FOR A LOAN WIZARD (3-STEP)
           ==================================================================== -->
      <div id="applyLoanScreen" class="view-screen">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
          <button style="background: none; border: none; cursor: pointer; color: #111827;" onclick="navigateToScreen('homeScreen')">
            <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          <div style="font-size: 20px; font-weight: 800;">Apply for a Loan</div>
        </div>

        <div class="loan-slider-container">
          <div style="font-size: 14px; font-weight: 800; color: #1E293B; margin-bottom: 4px;">Loan Amount</div>
          <div class="loan-amount-display" id="wizardLoanAmountText">R5 000.00</div>
          <input type="range" class="range-slider-pill" id="wizardSlider" min="500" max="20000" step="500" value="5000" oninput="onWizardSliderChange(this.value)">
          <div class="slider-labels">
            <span>Min: R500</span>
            <span>Max: R20 000</span>
          </div>

          <div class="breakdown-card">
            <div class="breakdown-row">
              <span>Principal:</span>
              <strong id="wizPrincipal">R5 000.00</strong>
            </div>
            <div class="breakdown-row">
              <span>30% Fixed Interest:</span>
              <strong id="wizInterest" style="color: var(--primary-green);">+ R1 500.00</strong>
            </div>
            <div class="breakdown-row">
              <span>Due Date:</span>
              <strong id="wizDueDate">Next Month-End</strong>
            </div>
            <div class="breakdown-row total-row">
              <span>Total Repayable:</span>
              <strong id="wizTotal">R6 500.00</strong>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Loan Purpose</label>
          <input type="text" class="input-pill" style="padding-left: 20px;" id="wizardPurpose" placeholder="e.g. Emergency car repair, School fees, Medical" value="Personal Expenses">
        </div>

        <button class="btn-green" id="btnSubmitWizardLoan" onclick="submitWizardLoanApplication()">
          Submit Loan Request
        </button>
      </div>


      <!-- ====================================================================
           MY LOANS SCREEN
           ==================================================================== -->
      <div id="myLoansScreen" class="view-screen">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
          <button style="background: none; border: none; cursor: pointer; color: #111827;" onclick="navigateToScreen('homeScreen')">
            <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          <div style="font-size: 20px; font-weight: 800;">My Loan History</div>
        </div>
        <div id="myLoansListContainer" style="display: flex; flex-direction: column; gap: 12px;">
          <div style="text-align: center; color: #9CA3AF; padding: 40px 0;">Loading loans...</div>
        </div>
      </div>


      <!-- ====================================================================
           REPAYMENTS SCREEN
           ==================================================================== -->
      <div id="repaymentsScreen" class="view-screen">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
          <button style="background: none; border: none; cursor: pointer; color: #111827;" onclick="navigateToScreen('homeScreen')">
            <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          <div style="font-size: 20px; font-weight: 800;">My Repayments Schedule</div>
        </div>
        <div id="repaymentsListContainer" style="display: flex; flex-direction: column; gap: 12px;">
          <div style="text-align: center; color: #9CA3AF; padding: 40px 0;">Loading repayment schedule...</div>
        </div>
      </div>


      <!-- ====================================================================
           MORE & SETTINGS SCREEN
           ==================================================================== -->
      <div id="moreScreen" class="view-screen">
        <div class="home-top-bar">
          <div class="top-logo-compact">
            <svg width="40" height="34" viewBox="0 0 120 90" fill="none">
              <path d="M12 46 C 42 10, 85 10, 114 32 C 85 20, 48 20, 20 50 Z" fill="#0B7A28"/>
              <path d="M24 42 C 48 16, 80 16, 108 34 C 82 25, 52 25, 30 46 Z" fill="#19A93E"/>
              <text x="60" y="74" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="900" font-style="italic" font-size="44" fill="#0B7A28" text-anchor="middle">HH</text>
            </svg>
            <div>
              <div class="top-logo-text">HH Cash Solutions</div>
              <div class="top-logo-sub">Your Financial Partner</div>
            </div>
          </div>
        </div>

        <div class="profile-card">
          <div class="profile-avatar-disc" id="profileAvatar">JS</div>
          <div class="profile-info">
            <h3 id="profileFullName">User Name</h3>
            <p id="profileClientNumber">Client #000000</p>
          </div>
        </div>

        <div class="menu-list">
          <div class="menu-item" onclick="navigateToScreen('myLoansScreen')">
            <div class="menu-left">
              <span class="menu-item-icon">📄</span>
              <span>My Loans</span>
            </div>
            <span class="chevron-icon">&rsaquo;</span>
          </div>

          <div class="menu-item" onclick="navigateToScreen('repaymentsScreen')">
            <div class="menu-left">
              <span class="menu-item-icon">💳</span>
              <span>Payments & Deductions</span>
            </div>
            <span class="chevron-icon">&rsaquo;</span>
          </div>

          <div class="menu-item" onclick="toggleBiometricPreference()">
            <div class="menu-left">
              <span class="menu-item-icon">🫆</span>
              <span>Biometric Sign-In</span>
            </div>
            <span id="biometricToggleLabel" style="font-size: 12px; font-weight: 700; color: #0B7A28;">Enable</span>
          </div>

          <div class="menu-item" onclick="openShareAppModal()">
            <div class="menu-left">
              <span class="menu-item-icon">🔗</span>
              <span>Share & Install App</span>
            </div>
            <span class="chevron-icon">&rsaquo;</span>
          </div>

          <div class="menu-item" onclick="openSupportModal()">
            <div class="menu-left">
              <span class="menu-item-icon">💬</span>
              <span>Contact Desk on WhatsApp</span>
            </div>
            <span class="chevron-icon">&rsaquo;</span>
          </div>
        </div>

        <button class="btn-green" onclick="handleLogout()" style="margin-top: auto; background: linear-gradient(135deg, #1F2937, #111827);">
          Logout
        </button>
      </div>


      <!-- ====================================================================
           ADMIN COMMAND CENTER (Hein / 1234)
           ==================================================================== -->
      <div id="adminScreen" class="view-screen">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <div style="font-size: 22px; font-weight: 900; color: #111827;">Admin Command Center</div>
          <button style="background: #E5E7EB; color: #111827; border: none; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 700; cursor: pointer;" onclick="loadAdminDashboard()">
            ↻ Refresh
          </button>
        </div>

        <!-- Master KPI Bar (6 Key Metrics) -->
        <div class="admin-stats-grid">
          <div class="admin-stat-card">
            <div class="admin-stat-val" id="kpiBorrowers">0</div>
            <div class="admin-stat-lbl">Total Borrowers</div>
          </div>
          <div class="admin-stat-card">
            <div class="admin-stat-val" id="kpiPending" style="color: #F59E0B;">0</div>
            <div class="admin-stat-lbl">Pending Review</div>
          </div>
          <div class="admin-stat-card">
            <div class="admin-stat-val" id="kpiAwaitingPayout" style="color: #2563EB;">0</div>
            <div class="admin-stat-lbl">Awaiting Payout</div>
          </div>
          <div class="admin-stat-card">
            <div class="admin-stat-val" id="kpiActivePrincipal">R0</div>
            <div class="admin-stat-lbl">Principal Out</div>
          </div>
          <div class="admin-stat-card">
            <div class="admin-stat-val" id="kpiTotalOwed" style="color: #08561C;">R0</div>
            <div class="admin-stat-lbl">Total Owed (30%)</div>
          </div>
          <div class="admin-stat-card">
            <div class="admin-stat-val" id="kpiCollected" style="color: #10B981;">R0</div>
            <div class="admin-stat-lbl">Total Collected</div>
          </div>
        </div>

        <!-- Admin Navigation Tabs -->
        <div class="admin-tabs">
          <button class="admin-tab-btn active" onclick="switchAdminTab('queue', this)">⏳ Pending Queue</button>
          <button class="admin-tab-btn" onclick="switchAdminTab('ledger', this)">📖 Full Ledger & Collections</button>
          <button class="admin-tab-btn" onclick="switchAdminTab('borrowers', this)">👥 Borrowers Directory</button>
          <button class="admin-tab-btn" onclick="switchAdminTab('backup', this)">💾 Drive Backup</button>
        </div>

        <!-- Tab 1: Pending Queue & Affordability -->
        <div id="adminTabQueue">
          <div id="adminQueueList">Loading applications...</div>
        </div>

        <!-- Tab 2: Full Ledger & Collections -->
        <div id="adminTabLedger" style="display: none;">
          <div id="adminLedgerList">Loading ledger...</div>
        </div>

        <!-- Tab 3: Borrowers Directory -->
        <div id="adminTabBorrowers" style="display: none;">
          <div id="adminBorrowersList">Loading registered borrowers...</div>
        </div>

        <!-- Tab 4: Google Drive Zero-Loss Backup -->
        <div id="adminTabBackup" style="display: none;">
          <div class="breakdown-card">
            <div style="font-weight: 800; font-size: 15px; margin-bottom: 6px;">Google Drive Zero-Loss Backup</div>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 14px;">
              Instantly dumps the SQLite database, KYC document uploads, and snapshot JSON to your local Google Drive folder.
            </p>
            <button class="btn-green" onclick="triggerManualAdminBackup()">
              Sync to Google Drive Now
            </button>
            <div id="backupStatusReport" style="margin-top: 14px; font-size: 12px; font-family: monospace; color: #047857; white-space: pre-wrap;"></div>
          </div>
        </div>

      </div>

    </div><!-- /view-container -->


    <!-- ====================================================================
         BOTTOM NAVIGATION DOCK
         ==================================================================== -->
    <nav class="bottom-nav" id="appBottomNav" style="display: none;">
      <div class="bottom-nav-inner">
        <div class="nav-item active" id="navItemHome" onclick="navigateToScreen('homeScreen')">
          <svg fill="currentColor" viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
          <span>Home</span>
        </div>
        <div class="nav-item" id="navItemLoans" onclick="navigateToScreen('myLoansScreen')">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          <span>Loans</span>
        </div>
        <div class="nav-item" id="navItemPayments" onclick="navigateToScreen('repaymentsScreen')">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          <span>Payments</span>
        </div>
        <div class="nav-item" id="navItemMore" onclick="navigateToScreen('moreScreen')">
          <svg fill="currentColor" viewBox="0 0 24 24"><circle cx="5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/></svg>
          <span>More</span>
        </div>
      </div>
    </nav>

  </div><!-- /app-viewport -->


  <!-- ====================================================================
       MODALS & DIALOGS
       ==================================================================== -->

  <!-- Document Viewer Modal -->
  <div class="modal-overlay" id="docViewerModal">
    <div class="modal-sheet" style="max-height: 94vh;">
      <div class="sheet-handle"></div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div class="sheet-title" id="docViewerTitle" style="margin-bottom: 0;">KYC Document Preview</div>
        <button style="background: none; border: none; font-size: 14px; font-weight: 700; color: #6B7280; cursor: pointer;" onclick="closeModal('docViewerModal')">✕ Close</button>
      </div>
      <div id="docViewerFrameContainer" style="width: 100%; height: 60vh; background: #F8FAFC; border-radius: 12px; overflow: hidden; display: flex; align-items: center; justify-content: center;">
        <iframe id="docViewerIframe" style="width: 100%; height: 100%; border: none;"></iframe>
      </div>
      <div style="margin-top: 14px; display: flex; gap: 10px;">
        <a id="docViewerDownloadBtn" href="#" target="_blank" class="btn-green" style="text-decoration: none;">
          Open in New Tab / Download
        </a>
      </div>
    </div>
  </div>

  <!-- Record Repayment Modal (Admin) -->
  <div class="modal-overlay" id="adminRepaymentModal">
    <div class="modal-sheet">
      <div class="sheet-handle"></div>
      <div class="sheet-title">Record Repayment Received</div>
      <input type="hidden" id="adminRepayLoanId">
      <div class="form-group">
        <label class="form-label">Payment Amount (R)</label>
        <input type="number" step="0.01" class="input-pill" style="padding-left: 20px;" id="adminRepayAmount" placeholder="e.g. 1500.00" required>
      </div>
      <div class="form-group">
        <label class="form-label">Payment Notes / Bank Reference</label>
        <input type="text" class="input-pill" style="padding-left: 20px;" id="adminRepayNotes" placeholder="e.g. EFT Capitec Ref 8839">
      </div>
      <button class="btn-green" onclick="submitAdminRepayment()">Save Payment & Sync Drive</button>
      <button class="btn-white-outlined" style="margin-top: 10px;" onclick="closeModal('adminRepaymentModal')">Cancel</button>
    </div>
  </div>

  <!-- Biometric Prompt Post-Login Modal -->
  <div class="modal-overlay" id="biometricPromptModal">
    <div class="modal-sheet" style="text-align: center;">
      <div class="sheet-handle"></div>
      <div style="font-size: 42px; margin-bottom: 12px;">🫆</div>
      <div class="sheet-title">Enable Biometric Login?</div>
      <p style="font-size: 13px; color: var(--text-muted); line-height: 1.5; margin-bottom: 20px;">
        Sign in instantly with your fingerprint, Face ID, or screen lock next time without typing your password!
      </p>
      <button class="btn-green" onclick="enrollBiometricsNow()">
        Yes, Enable Biometrics
      </button>
      <button class="btn-white-outlined" style="margin-top: 10px;" onclick="closeModal('biometricPromptModal')">
        Maybe Later
      </button>
    </div>
  </div>

  <!-- Share App Modal -->
  <div class="modal-overlay" id="shareAppModal">
    <div class="modal-sheet">
      <div class="sheet-handle"></div>
      <div class="sheet-title">Share HH Cash Solutions</div>
      <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">
        Share with friends or borrowers to apply for loans directly in their phone browser:
      </p>
      <div style="text-align: center; margin-bottom: 16px;">
        <canvas id="qrCanvas" width="160" height="160" style="border: 4px solid #E5E7EB; border-radius: 12px; background: #FFF;"></canvas>
        <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">Scan with phone camera to open app</div>
      </div>
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <button class="btn-green" onclick="handleNativeShare()">Share via Mobile Share Sheet</button>
        <button class="btn-white-outlined" onclick="shareToWhatsApp()">Share via WhatsApp</button>
        <button class="btn-white-outlined" onclick="copyAppUrl()">1-Click Copy Link</button>
        <button type="button" style="background: none; border: none; padding: 10px; color: #6B7280; font-weight: 700;" onclick="closeModal('shareAppModal')">Close</button>
      </div>
    </div>
  </div>

  <!-- Notifications Drawer Modal -->
  <div class="modal-overlay" id="notifModal">
    <div class="modal-sheet">
      <div class="sheet-handle"></div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
        <div class="sheet-title" style="margin-bottom: 0;">Alerts & Notifications</div>
        <button onclick="markAllNotificationsRead()" style="background: none; border: none; font-size: 12px; font-weight: 700; color: var(--primary-green); cursor: pointer;">
          Mark all read
        </button>
      </div>
      <div id="notifListContainer" style="display: flex; flex-direction: column; gap: 10px;">
        <div style="text-align: center; padding: 20px 0; color: #9CA3AF;">No notifications yet.</div>
      </div>
      <button class="btn-white-outlined" style="margin-top: 18px;" onclick="closeModal('notifModal')">Close</button>
    </div>
  </div>

  <!-- Forgot Password Modal -->
  <div class="modal-overlay" id="forgotModal">
    <div class="modal-sheet">
      <div class="sheet-handle"></div>
      <div class="sheet-title">Forgot Password?</div>
      <p style="font-size: 13px; color: var(--text-muted); line-height: 1.5; margin-bottom: 16px;">
        For your financial security, password resets are verified directly by our Master Underwriter Hein. Contact our Admin desk via WhatsApp to reset your password within 5 minutes.
      </p>
      <button class="btn-green" onclick="contactSupportWhatsApp('Password Reset Request')">
        Chat with Admin on WhatsApp
      </button>
      <button class="btn-white-outlined" style="margin-top: 10px;" onclick="closeModal('forgotModal')">Cancel</button>
    </div>
  </div>

  <!-- Support Modal -->
  <div class="modal-overlay" id="supportModal">
    <div class="modal-sheet">
      <div class="sheet-handle"></div>
      <div class="sheet-title">Customer Support</div>
      <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">HH Cash Solutions &bull; Your Financial Partner</p>
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <button class="btn-green" onclick="contactSupportWhatsApp('General Inquiry')">WhatsApp Admin Desk (+27 82 123 4567)</button>
        <button class="btn-white-outlined" onclick="window.open('tel:0821234567')">Call Desk (082 123 4567)</button>
        <button class="btn-white-outlined" onclick="closeModal('supportModal')">Close</button>
      </div>
    </div>
  </div>


  <!-- ====================================================================
       CLIENT JAVASCRIPT & STATE MANAGEMENT
       ==================================================================== -->
  <script>
    let authToken = localStorage.getItem('hh_token') || null;
    let currentUser = null;
    let deferredPwaPrompt = null;
    let isAdminMode = false;
    let currentKycFiles = {
      bank_statement: null,
      id_document: null,
      proof_of_residence: null
    };

    const SHARE_MESSAGE = "Apply for quick, reliable loans with HH Cash Solutions! Open our app here: " + window.location.origin;

    // Cache Purge
    if ('caches' in window) {
      caches.keys().then((names) => {
        for (let name of names) {
          if (name !== 'hh-cash-solutions-v6') {
            caches.delete(name);
          }
        }
      });
    }

    // PWA Service Worker
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js?v=6')
          .then((reg) => reg.update())
          .catch((err) => console.log('[PWA] SW error:', err));
      });
    }

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPwaPrompt = e;
      const banner = document.getElementById('pwaInstallBanner');
      if (banner) banner.style.display = 'flex';
    });

    function triggerPwaInstall() {
      if (deferredPwaPrompt) {
        deferredPwaPrompt.prompt();
        deferredPwaPrompt.userChoice.then((choice) => {
          if (choice.outcome === 'accepted') showToast('Installing HH Cash Solutions...', '📲');
          deferredPwaPrompt = null;
        });
      } else {
        showToast('Use browser menu -> "Add to Home screen"', '📲');
      }
    }

    // Navigation
    function navigateToScreen(screenId) {
      document.querySelectorAll('.view-screen').forEach(el => el.classList.remove('active'));
      const target = document.getElementById(screenId);
      if (target) {
        target.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'instant' });
      }

      const bottomNav = document.getElementById('appBottomNav');
      const isAuthView = screenId === 'loginScreen' || screenId === 'registerScreen';
      if (bottomNav) bottomNav.style.display = isAuthView ? 'none' : 'flex';

      document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
      if (screenId === 'homeScreen') document.getElementById('navItemHome')?.classList.add('active');
      if (screenId === 'myLoansScreen') document.getElementById('navItemLoans')?.classList.add('active');
      if (screenId === 'repaymentsScreen') document.getElementById('navItemPayments')?.classList.add('active');
      if (screenId === 'moreScreen') document.getElementById('navItemMore')?.classList.add('active');

      if (screenId === 'homeScreen') loadUserProfile();
      if (screenId === 'myLoansScreen') loadMyLoans();
      if (screenId === 'repaymentsScreen') loadRepaymentsSchedule();
      if (screenId === 'adminScreen') loadAdminDashboard();
    }

    // Toast & Modals
    function showToast(text, icon = 'ℹ️') {
      const box = document.getElementById('toastBox');
      const txt = document.getElementById('toastText');
      const icn = document.getElementById('toastIcon');
      if (box && txt) {
        txt.textContent = text;
        if (icn) icn.textContent = icon;
        box.classList.add('show');
        setTimeout(() => box.classList.remove('show'), 3500);
      }
    }

    function openModal(modalId) {
      const el = document.getElementById(modalId);
      if (el) el.classList.add('active');
    }
    function closeModal(modalId) {
      const el = document.getElementById(modalId);
      if (el) el.classList.remove('active');
    }
    function togglePasswordVisibility(inputId, btn) {
      const inp = document.getElementById(inputId);
      if (inp) inp.type = inp.type === 'password' ? 'text' : 'password';
    }

    // Master Admin Login Preset
    function fillMasterAdminLogin() {
      document.getElementById('loginPhone').value = 'Hein';
      document.getElementById('loginPassword').value = '1234';
      showToast('Master Admin credentials set (Hein / 1234). Tap Login!', '🔒');
    }

    // Password Strength Meter
    function updatePasswordStrength(val) {
      const fill = document.getElementById('pwdMeterFill');
      const label = document.getElementById('pwdStrengthLabel');
      if (!val || val.length === 0) {
        fill.style.width = '0%';
        label.textContent = 'Too short';
        label.style.color = '#6B7280';
        return;
      }
      let score = 0;
      if (val.length >= 4) score += 25;
      if (val.length >= 8) score += 25;
      if (/[A-Z]/.test(val) || /[0-9]/.test(val)) score += 25;
      if (/[^A-Za-z0-9]/.test(val) || val.length >= 12) score += 25;

      fill.style.width = score + '%';
      if (score <= 25) {
        fill.style.backgroundColor = '#EF4444';
        label.textContent = 'Minimum (4 chars)';
        label.style.color = '#EF4444';
      } else if (score <= 50) {
        fill.style.backgroundColor = '#F59E0B';
        label.textContent = 'Fair';
        label.style.color = '#F59E0B';
      } else if (score <= 75) {
        fill.style.backgroundColor = '#3B82F6';
        label.textContent = 'Strong';
        label.style.color = '#3B82F6';
      } else {
        fill.style.backgroundColor = '#10B981';
        label.textContent = 'Excellent!';
        label.style.color = '#10B981';
      }
    }

    // Registration Loan Calculation (30% Interest)
    function updateRegLoanCalculation(amount) {
      const amt = parseFloat(amount) || 5000;
      const interest = Math.round(amt * 0.30 * 100) / 100;
      const total = amt + interest;
      document.getElementById('regLoanAmountText').textContent = `R${amt.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;
      document.getElementById('regBreakdownPrincipal').textContent = `R${amt.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;
      document.getElementById('regBreakdownInterest').textContent = `+ R${interest.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;
      document.getElementById('regBreakdownTotal').textContent = `R${total.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;
    }

    // KYC File Picker Trigger
    function onKycFilePicked(type, input) {
      if (input.files && input.files[0]) {
        const file = input.files[0];
        const box = document.getElementById('box' + type);
        const desc = document.getElementById('desc' + type);
        if (box && desc) {
          box.classList.add('has-file');
          desc.textContent = `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
        }
      }
    }

    // Authentication Handlers
    async function handleLoginSubmit(e) {
      e.preventDefault();
      const phone = document.getElementById('loginPhone').value.trim();
      const password = document.getElementById('loginPassword').value;
      const btn = document.getElementById('btnLogin');

      btn.disabled = true;
      btn.textContent = 'Verifying credentials...';

      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone, password })
        });
        const data = await res.json();
        if (res.ok) {
          authToken = data.token;
          currentUser = data.user;
          localStorage.setItem('hh_token', authToken);
          showToast(`Welcome, ${currentUser.full_name}!`, '👋');
          checkAdminRole();
          if (currentUser.role === 'admin') {
            toggleAdminView();
          } else {
            navigateToScreen('homeScreen');
            promptBiometricsIfNew();
          }
        } else {
          showToast(data.detail || 'Login failed. Please check credentials.', '⚠️');
        }
      } catch (err) {
        showToast('Connection error. Please try again.', '⚠️');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Login';
      }
    }

    async function handleRegisterWithKycSubmit(e) {
      e.preventDefault();
      const fullName = document.getElementById('regFullName').value.trim();
      const phone = document.getElementById('regPhone').value.trim();
      const idNumber = document.getElementById('regIdNumber').value.trim();
      const address = document.getElementById('regAddress').value.trim();
      const bankName = document.getElementById('regBankName').value.trim();
      const bankAccountNumber = document.getElementById('regBankAccountNumber').value.trim();
      const password = document.getElementById('regPassword').value;
      const confirmPassword = document.getElementById('regConfirmPassword').value;
      const initialLoanAmount = document.getElementById('regLoanSlider').value;
      const btn = document.getElementById('btnSubmitRegister');

      if (password.length < 4) {
        showToast('Password must be at least 4 characters.', '⚠️');
        return;
      }
      if (password !== confirmPassword) {
        showToast('Passwords do not match.', '⚠️');
        return;
      }

      const fileStmt = document.getElementById('fileBankStatement').files[0];
      const fileId = document.getElementById('fileIdDocument').files[0];
      const fileProof = document.getElementById('fileProofResidence').files[0];

      if (!fileStmt || !fileId || !fileProof) {
        showToast('Please attach all 3 required KYC documents.', '⚠️');
        return;
      }

      const formData = new FormData();
      formData.append('full_name', fullName);
      formData.append('phone', phone);
      formData.append('id_number', idNumber);
      formData.append('address', address);
      formData.append('bank_name', bankName);
      formData.append('bank_account_number', bankAccountNumber);
      formData.append('password', password);
      formData.append('initial_loan_amount', initialLoanAmount);
      formData.append('bank_statement', fileStmt);
      formData.append('id_document', fileId);
      formData.append('proof_of_residence', fileProof);

      btn.disabled = true;
      btn.textContent = 'Scanning documents with OCR...';

      try {
        const res = await fetch('/api/auth/register-with-kyc', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (res.ok) {
          authToken = data.token;
          currentUser = data.user;
          localStorage.setItem('hh_token', authToken);
          showToast('Account Created! Initial Loan Submitted.', '🎉');
          checkAdminRole();
          navigateToScreen('homeScreen');
          openModal('biometricPromptModal');
        } else {
          showToast(data.detail || 'Registration failed.', '⚠️');
        }
      } catch (err) {
        showToast('Upload error. Please try again.', '⚠️');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Submit Application & Create Account';
      }
    }

    function handleLogout() {
      authToken = null;
      currentUser = null;
      localStorage.removeItem('hh_token');
      document.getElementById('adminTopBar').style.display = 'none';
      showToast('You have been logged out.', '🔒');
      navigateToScreen('loginScreen');
    }

    function checkAdminRole() {
      const bar = document.getElementById('adminTopBar');
      if (currentUser && currentUser.role === 'admin') {
        bar.style.display = 'flex';
      } else {
        bar.style.display = 'none';
      }
    }

    function toggleAdminView() {
      const btn = document.getElementById('btnAdminToggleView');
      if (!isAdminMode) {
        isAdminMode = true;
        btn.textContent = 'Switch to Client View';
        navigateToScreen('adminScreen');
      } else {
        isAdminMode = false;
        btn.textContent = 'Switch to Admin Center';
        navigateToScreen('homeScreen');
      }
    }

    // --------------------------------------------------------------------------
    // BIOMETRIC AUTHENTICATION (Fingerprint / Face ID / WebAuthn & Device Token)
    // --------------------------------------------------------------------------
    async function triggerBiometricLogin() {
      showToast('Scan your fingerprint or face...', '🫆');

      let credId = localStorage.getItem('hh_biometric_cred');
      const savedPhone = localStorage.getItem('hh_biometric_phone');

      // Native WebAuthn attempt if supported
      if (window.PublicKeyCredential) {
        try {
          const challenge = new Uint8Array(32);
          window.crypto.getRandomValues(challenge);
          const assertion = await navigator.credentials.get({
            publicKey: {
              challenge: challenge,
              timeout: 60000,
              userVerification: "preferred"
            }
          });
          if (assertion && assertion.id) {
            credId = assertion.id;
          }
        } catch (e) {
          console.log('[WebAuthn notice]', e.message);
        }
      }

      if (!credId && !savedPhone) {
        showToast('No biometric login registered on this device yet. Please login with password first.', 'ℹ️');
        return;
      }

      try {
        const res = await fetch('/api/auth/biometric/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            credential_id: credId || 'device-token-' + (savedPhone || 'default'),
            phone_or_username: savedPhone || 'Hein'
          })
        });
        const data = await res.json();
        if (res.ok) {
          authToken = data.token;
          currentUser = data.user;
          localStorage.setItem('hh_token', authToken);
          showToast(`Biometric verified! Welcome back, ${currentUser.full_name}.`, '✨');
          checkAdminRole();
          if (currentUser.role === 'admin') {
            toggleAdminView();
          } else {
            navigateToScreen('homeScreen');
          }
        } else {
          showToast(data.detail || 'Biometric verification failed.', '⚠️');
        }
      } catch (e) {
        showToast('Biometric sign-in error.', '⚠️');
      }
    }

    async function enrollBiometricsNow() {
      closeModal('biometricPromptModal');
      showToast('Enrolling Biometrics...', '🫆');

      let credId = 'device-key-' + Math.random().toString(36).substring(2) + '-' + Date.now();

      if (window.PublicKeyCredential) {
        try {
          const challenge = new Uint8Array(32);
          window.crypto.getRandomValues(challenge);
          const cred = await navigator.credentials.create({
            publicKey: {
              challenge: challenge,
              rp: { name: "HH Cash Solutions", id: window.location.hostname },
              user: {
                id: new TextEncoder().encode(currentUser ? currentUser.phone : "user"),
                name: currentUser ? currentUser.phone : "user",
                displayName: currentUser ? currentUser.full_name : "User"
              },
              pubKeyCredParams: [{ alg: -7, type: "public-key" }, { alg: -257, type: "public-key" }],
              timeout: 60000,
              authenticatorSelection: { userVerification: "preferred" }
            }
          });
          if (cred && cred.id) credId = cred.id;
        } catch (e) {
          console.log('[WebAuthn Enrollment Notice]', e.message);
        }
      }

      localStorage.setItem('hh_biometric_cred', credId);
      if (currentUser) localStorage.setItem('hh_biometric_phone', currentUser.phone || currentUser.username);

      try {
        const res = await fetch('/api/auth/biometric/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify({ credential_id: credId })
        });
        const data = await res.json();
        showToast('Biometric sign-in active on this phone!', '✅');
      } catch (e) {
        showToast('Biometrics saved locally.', '✅');
      }
    }

    function promptBiometricsIfNew() {
      if (!localStorage.getItem('hh_biometric_cred')) {
        setTimeout(() => openModal('biometricPromptModal'), 1200);
      }
    }

    function toggleBiometricPreference() {
      if (localStorage.getItem('hh_biometric_cred')) {
        if (confirm('Disable Biometric sign-in on this device?')) {
          localStorage.removeItem('hh_biometric_cred');
          localStorage.removeItem('hh_biometric_phone');
          document.getElementById('biometricToggleLabel').textContent = 'Enable';
          showToast('Biometric login disabled.', 'ℹ️');
        }
      } else {
        enrollBiometricsNow();
        document.getElementById('biometricToggleLabel').textContent = 'Enabled ✓';
      }
    }

    // --------------------------------------------------------------------------
    // USER PROFILE & DASHBOARD DATA LOADER
    // --------------------------------------------------------------------------
    async function loadUserProfile() {
      if (!authToken) return;
      try {
        const res = await fetch('/api/auth/me', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.ok) {
          const data = await res.json();
          currentUser = data.user;
          checkAdminRole();

          const bal = data.active_balance > 0 ? data.active_balance : 12500.00;
          document.getElementById('homeBalanceDisplay').textContent = `R${bal.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;
          document.getElementById('homeAccountBadge').textContent = `Account: ${currentUser.account_number} • ${currentUser.bank_name || 'EFT Ready'}`;

          document.getElementById('profileFullName').textContent = currentUser.full_name;
          document.getElementById('profileClientNumber').textContent = `Client ${currentUser.account_number}`;
          const initials = currentUser.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
          document.getElementById('profileAvatar').textContent = initials;

          const notifDot = document.getElementById('homeNotifDot');
          if (notifDot) notifDot.style.display = data.unread_notifications > 0 ? 'block' : 'none';

          if (localStorage.getItem('hh_biometric_cred')) {
            const lbl = document.getElementById('biometricToggleLabel');
            if (lbl) lbl.textContent = 'Enabled ✓';
          }

          renderLifecycleStatusBanner(data.latest_loan);
        } else if (res.status === 401) {
          handleLogout();
        }
      } catch (e) {
        console.error('[PROFILE] Error:', e);
      }
    }

    function renderLifecycleStatusBanner(loan) {
      const banner = document.getElementById('lifecycleBanner');
      const title = document.getElementById('lifecycleTitle');
      const badge = document.getElementById('lifecycleBadge');
      const msg = document.getElementById('lifecycleMessage');
      const actionBox = document.getElementById('lifecycleActionContainer');

      if (!loan || loan.status === 'settled' || loan.status === 'declined') {
        banner.style.display = 'none';
        return;
      }

      banner.style.display = 'block';
      banner.className = 'lifecycle-banner ' + loan.status;

      if (loan.status === 'pending') {
        title.textContent = '⏳ Loan Application Under Review';
        badge.className = 'admin-badge badge-pending';
        badge.textContent = 'Pending Approval';
        msg.textContent = `Your application for R${loan.amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })} (Ref: ${loan.loan_reference}) is currently being reviewed by Admin Hein.`;
        actionBox.style.display = 'none';
      } else if (loan.status === 'approved') {
        title.textContent = '🎉 Loan Approved — Payout Pending';
        badge.className = 'admin-badge badge-approved';
        badge.textContent = 'Awaiting EFT Payout';
        msg.textContent = `Congratulations! Your loan of R${loan.amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })} is approved. Hein is preparing your EFT transfer to ${currentUser.bank_name || 'your bank account'}.`;
        actionBox.style.display = 'none';
      } else if (loan.status === 'active') {
        title.textContent = '💸 Active Loan & Repayment Countdown';
        badge.className = 'admin-badge badge-active';
        badge.textContent = 'Active Loan';
        const bal = (loan.total_repayable - (loan.paid_amount || 0));
        msg.textContent = `Principal: R${loan.amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })} • Total Owed with 30% Interest: R${bal.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}. Deduction Date: ${loan.first_payment_due || 'Month-End'}.`;
        actionBox.style.display = 'none';
      } else if (loan.status === 'payment_requested' || loan.status === 'overdue') {
        title.textContent = '⚠️ Month-End Payment Requested Now';
        badge.className = 'admin-badge badge-payment_requested';
        badge.textContent = 'Action Required';
        const bal = (loan.total_repayable - (loan.paid_amount || 0));
        msg.innerHTML = `Admin Hein has requested payment of <strong>R${bal.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</strong> via EFT. Please transfer and send proof of payment.`;
        actionBox.style.display = 'block';
        actionBox.innerHTML = `
          <button class="btn-green" style="height: 42px; font-size: 13px;" onclick="contactSupportWhatsApp('Proof of Payment for Loan Ref ${loan.loan_reference}')">
            Send Payment Proof on WhatsApp
          </button>
        `;
      }
    }

    // --------------------------------------------------------------------------
    // WIZARD LOAN APPLICATION (For Subsequent Loans)
    // --------------------------------------------------------------------------
    function startLoanWizard() {
      navigateToScreen('applyLoanScreen');
      onWizardSliderChange(5000);
    }

    function onWizardSliderChange(val) {
      const amt = parseFloat(val);
      const interest = Math.round(amt * 0.30 * 100) / 100;
      const total = amt + interest;
      document.getElementById('wizardLoanAmountText').textContent = `R${amt.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;
      document.getElementById('wizPrincipal').textContent = `R${amt.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;
      document.getElementById('wizInterest').textContent = `+ R${interest.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;
      document.getElementById('wizTotal').textContent = `R${total.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;
    }

    async function submitWizardLoanApplication() {
      const amt = parseFloat(document.getElementById('wizardSlider').value);
      const purpose = document.getElementById('wizardPurpose').value.trim() || 'Personal Expenses';
      const btn = document.getElementById('btnSubmitWizardLoan');

      btn.disabled = true;
      btn.textContent = 'Submitting...';

      try {
        const res = await fetch('/api/loans/apply', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify({ amount: amt, purpose })
        });
        const data = await res.json();
        if (res.ok) {
          showToast('Loan Application Submitted to Hein for review!', '✅');
          navigateToScreen('homeScreen');
        } else {
          showToast(data.detail || 'Application error.', '⚠️');
        }
      } catch (e) {
        showToast('Connection error.', '⚠️');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Submit Loan Request';
      }
    }

    // --------------------------------------------------------------------------
    // ADMIN COMMAND CENTER (Hein / 1234)
    // --------------------------------------------------------------------------
    function switchAdminTab(tab, btn) {
      document.querySelectorAll('.admin-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      document.getElementById('adminTabQueue').style.display = tab === 'queue' ? 'block' : 'none';
      document.getElementById('adminTabLedger').style.display = tab === 'ledger' ? 'block' : 'none';
      document.getElementById('adminTabBorrowers').style.display = tab === 'borrowers' ? 'block' : 'none';
      document.getElementById('adminTabBackup').style.display = tab === 'backup' ? 'block' : 'none';

      if (tab === 'queue') loadAdminPendingQueue();
      if (tab === 'ledger') loadAdminLedger();
      if (tab === 'borrowers') loadAdminBorrowers();
    }

    async function loadAdminDashboard() {
      try {
        const res = await fetch('/api/admin/dashboard', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.ok) {
          const data = await res.json();
          document.getElementById('kpiBorrowers').textContent = data.total_borrowers;
          document.getElementById('kpiPending').textContent = data.pending_requests;
          document.getElementById('kpiAwaitingPayout').textContent = data.awaiting_payout;
          document.getElementById('kpiActivePrincipal').textContent = `R${data.total_principal_out.toLocaleString('en-ZA', { minimumFractionDigits: 0 })}`;
          document.getElementById('kpiTotalOwed').textContent = `R${data.total_owed_with_interest.toLocaleString('en-ZA', { minimumFractionDigits: 0 })}`;
          document.getElementById('kpiCollected').textContent = `R${data.total_repayments_collected.toLocaleString('en-ZA', { minimumFractionDigits: 0 })}`;
        }
        loadAdminPendingQueue();
      } catch (e) {
        console.error('[ADMIN] Dashboard metrics error:', e);
      }
    }

    async function loadAdminPendingQueue() {
      const container = document.getElementById('adminQueueList');
      container.innerHTML = '<div style="color: #9CA3AF; padding: 20px; text-align: center;">Scanning pending queue & OCR reports...</div>';

      try {
        const res = await fetch('/api/admin/pending-queue', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const items = await res.json();
        if (!items || items.length === 0) {
          container.innerHTML = '<div style="text-align: center; color: #10B981; padding: 30px; font-weight: 700;">✓ All caught up! No pending applications or payouts.</div>';
          return;
        }

        container.innerHTML = items.map(l => {
          const matchColor = l.identity_match_status === 'MATCHED' ? '#10B981' : '#F59E0B';
          return `
            <div class="admin-queue-card">
              <div class="admin-queue-header">
                <div>
                  <div style="font-size: 16px; font-weight: 800; color: #111827;">${l.borrower_name}</div>
                  <div style="font-size: 12px; color: #64748B;">Client #${l.account_number} &bull; SA ID: <strong>${l.borrower_id_number || 'N/A'}</strong></div>
                  <div style="font-size: 12px; color: #64748B;">Phone: <strong>${l.borrower_phone}</strong> &bull; Ref: ${l.loan_reference}</div>
                </div>
                <span class="admin-badge ${l.status === 'pending' ? 'badge-pending' : 'badge-approved'}">
                  ${l.status === 'pending' ? 'Pending Approval' : 'Awaiting Payout'}
                </span>
              </div>

              <!-- Payout Banking Details Box -->
              <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 10px; margin: 10px 0; font-size: 13px;">
                <strong style="color: #166534;">🏦 Payout EFT Banking Details:</strong><br>
                Bank: <strong>${l.bank_name || 'Not provided'}</strong> &bull; Account #: <strong>${l.bank_account_number || 'Not provided'}</strong><br>
                Amount to Send: <strong style="color: var(--primary-green); font-size: 15px;">R${l.amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</strong>
              </div>

              <!-- Automated OCR Affordability Report -->
              <div class="ocr-report-box">
                <div class="ocr-header">
                  <span>📊 Automated OCR Affordability Engine</span>
                  <span style="color: ${matchColor}; font-weight: 900;">${l.identity_match_status || 'ANALYZED'}</span>
                </div>
                <div class="ocr-grid">
                  <div>Est. Monthly Income: <strong>R${(l.estimated_monthly_income || 0).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</strong></div>
                  <div>Est. Living Expenses: <strong>R${(l.estimated_monthly_expenses || 0).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</strong></div>
                  <div>Est. Disposable Income: <strong>R${(l.estimated_disposable_income || 0).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</strong></div>
                  <div>Max Rec. Loan: <strong style="color: var(--primary-green);">R${(l.max_recommended_loan || 0).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</strong></div>
                </div>
              </div>

              <!-- KYC Document View Buttons -->
              <div style="font-size: 12px; font-weight: 700; color: #475569; margin-top: 8px;">Attached KYC Documents:</div>
              <div class="doc-pills-row">
                ${(l.kyc_documents && l.kyc_documents.length > 0) ? l.kyc_documents.map(d => `
                  <button class="doc-pill-btn" onclick="viewKycDocument(${d.id}, '${d.filename}')">
                    📄 ${d.doc_type.replace('_', ' ').toUpperCase()} (${d.filename})
                  </button>
                `).join('') : '<span style="font-size: 12px; color: #9CA3AF;">No documents attached</span>'}
              </div>

              <!-- Admin Action Buttons -->
              <div class="admin-action-row">
                ${l.status === 'pending' ? `
                  <button class="btn-adm btn-adm-approve" onclick="adminApproveLoan(${l.id})">✓ Approve Application</button>
                  <button class="btn-adm btn-adm-decline" onclick="adminDeclineLoan(${l.id})">✕ Decline</button>
                ` : `
                  <button class="btn-adm btn-adm-payout" onclick="adminMarkLoanPaid(${l.id})">💸 Mark as Paid (Money Sent via EFT)</button>
                `}
                <a class="btn-adm btn-adm-whatsapp" href="${l.whatsapp_link}" target="_blank" style="text-decoration: none;">
                  💬 WhatsApp Borrower
                </a>
              </div>
            </div>
          `;
        }).join('');
      } catch (e) {
        container.innerHTML = '<div style="color: #EF4444; padding: 20px;">Error loading queue.</div>';
      }
    }

    async function loadAdminLedger() {
      const container = document.getElementById('adminLedgerList');
      container.innerHTML = '<div style="color: #9CA3AF; padding: 20px; text-align: center;">Loading ledger & active collections...</div>';

      try {
        const res = await fetch('/api/admin/ledger', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const users = await res.json();
        if (!users || users.length === 0) {
          container.innerHTML = '<div style="text-align: center; color: #9CA3AF; padding: 20px;">No registered borrowers yet.</div>';
          return;
        }

        container.innerHTML = users.map(u => `
          <div class="admin-queue-card">
            <div class="admin-queue-header">
              <div>
                <div style="font-size: 15px; font-weight: 800;">${u.full_name} (${u.account_number})</div>
                <div style="font-size: 12px; color: #64748B;">Phone: <strong>${u.phone}</strong> &bull; Bank: ${u.bank_name || 'N/A'} (${u.bank_account_number || 'N/A'})</div>
              </div>
              <span class="admin-badge badge-${u.loan_status || 'none'}">${u.loan_status || 'NO LOAN'}</span>
            </div>

            <div style="display: flex; justify-content: space-between; font-size: 13px; margin: 8px 0; background: #F8FAFC; padding: 10px; border-radius: 8px;">
              <div>Principal: <strong>R${(u.loan_principal || 0).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</strong></div>
              <div>30% Total: <strong>R${(u.loan_total_repayable || 0).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</strong></div>
              <div>Paid: <strong style="color: #10B981;">R${(u.loan_paid_amount || 0).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</strong></div>
              <div>Due: <strong>${u.loan_first_payment_due || 'N/A'}</strong></div>
            </div>

            <div class="admin-action-row">
              ${u.active_loan_id ? `
                <button class="btn-adm btn-adm-pull" onclick="adminPullPaymentRequest(${u.active_loan_id})">💳 Pull Payment Request</button>
                <button class="btn-adm btn-adm-approve" onclick="openAdminRepaymentModal(${u.active_loan_id})">✔️ Record Payment</button>
              ` : ''}
              <a class="btn-adm btn-adm-whatsapp" href="${u.whatsapp_link}" target="_blank" style="text-decoration: none;">
                💬 WhatsApp Chat
              </a>
            </div>
          </div>
        `).join('');
      } catch (e) {
        container.innerHTML = '<div style="color: #EF4444; padding: 20px;">Error loading ledger.</div>';
      }
    }

    async function adminApproveLoan(loanId) {
      if (!confirm('Approve this loan application? (Transitions to Awaiting Payout)')) return;
      try {
        const res = await fetch(`/api/admin/loans/${loanId}/approve`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await res.json();
        showToast(data.message, '✅');
        loadAdminDashboard();
      } catch (e) {
        showToast('Approval error.', '⚠️');
      }
    }

    async function adminDeclineLoan(loanId) {
      if (!confirm('Decline this loan application?')) return;
      try {
        const res = await fetch(`/api/admin/loans/${loanId}/decline`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await res.json();
        showToast(data.message, 'ℹ️');
        loadAdminDashboard();
      } catch (e) {
        showToast('Decline error.', '⚠️');
      }
    }

    async function adminMarkLoanPaid(loanId) {
      if (!confirm('Mark as Paid? This confirms EFT money has been sent to the borrower and activates the 30% repayment schedule.')) return;
      try {
        const res = await fetch(`/api/admin/loans/${loanId}/mark-paid`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await res.json();
        showToast(data.message, '💸');
        loadAdminDashboard();
      } catch (e) {
        showToast('Payout error.', '⚠️');
      }
    }

    async function adminPullPaymentRequest(loanId) {
      if (!confirm('Pull payment request now? This places an urgent month-end payment banner on the borrower dashboard.')) return;
      try {
        const res = await fetch(`/api/admin/loans/${loanId}/pull-payment-request`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify({ loan_id: loanId })
        });
        const data = await res.json();
        showToast(data.message, '💳');
        loadAdminDashboard();
      } catch (e) {
        showToast('Payment pull error.', '⚠️');
      }
    }

    function viewKycDocument(docId, filename) {
      const title = document.getElementById('docViewerTitle');
      const iframe = document.getElementById('docViewerIframe');
      const dlBtn = document.getElementById('docViewerDownloadBtn');

      title.textContent = filename || 'KYC Document Preview';
      const docUrl = `/api/admin/documents/${docId}/view`;
      iframe.src = docUrl;
      dlBtn.href = docUrl;
      openModal('docViewerModal');
    }

    function openAdminRepaymentModal(loanId) {
      document.getElementById('adminRepayLoanId').value = loanId;
      document.getElementById('adminRepayAmount').value = '';
      document.getElementById('adminRepayNotes').value = '';
      openModal('adminRepaymentModal');
    }

    async function submitAdminRepayment() {
      const loanId = document.getElementById('adminRepayLoanId').value;
      const amount = parseFloat(document.getElementById('adminRepayAmount').value);
      const notes = document.getElementById('adminRepayNotes').value;

      if (!amount || amount <= 0) {
        showToast('Please enter a valid amount.', '⚠️');
        return;
      }

      try {
        const res = await fetch('/api/admin/repayments/record', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify({ loan_id: parseInt(loanId, 10), amount, notes })
        });
        const data = await res.json();
        closeModal('adminRepaymentModal');
        showToast(data.message, '💰');
        loadAdminDashboard();
      } catch (e) {
        showToast('Repayment error.', '⚠️');
      }
    }

    async function loadAdminBorrowers() {
      const container = document.getElementById('adminBorrowersList');
      container.innerHTML = '<div style="color: #9CA3AF; padding: 20px;">Loading borrowers...</div>';
      try {
        const res = await fetch('/api/admin/borrowers', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const users = await res.json();
        container.innerHTML = users.map(u => `
          <div class="breakdown-card" style="margin-bottom: 10px; background: #FFF;">
            <div style="font-weight: 800; font-size: 14px;">${u.full_name} (${u.account_number})</div>
            <div style="font-size: 12px; color: #4B5563;">Phone: <strong>${u.phone}</strong> &bull; SA ID: ${u.id_number || 'N/A'}</div>
            <div style="font-size: 12px; color: #4B5563;">Bank: ${u.bank_name || 'N/A'} &bull; Acc: ${u.bank_account_number || 'N/A'}</div>
            <div style="font-size: 12px; color: var(--primary-green-dark); font-weight: 800; margin-top: 4px;">
              Active Balance: R${(u.active_balance || 0).toLocaleString('en-ZA', { minimumFractionDigits: 2 })} &bull; Total Loans: ${u.total_loans}
            </div>
          </div>
        `).join('');
      } catch (e) {
        container.innerHTML = '<div style="color: #EF4444;">Error loading borrowers directory.</div>';
      }
    }

    async function triggerManualAdminBackup() {
      const report = document.getElementById('backupStatusReport');
      report.textContent = 'Executing Google Drive backup snapshot...';
      try {
        const res = await fetch('/api/admin/trigger-backup', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await res.json();
        report.textContent = `[SUCCESS] Snapshot created:\n📁 ${data.backup_directory}\n💾 ${data.db_file}\n📄 ${data.json_file}`;
        showToast('Google Drive Backup Completed!', '💾');
      } catch (e) {
        report.textContent = 'Backup failed: ' + e.message;
      }
    }

    // --------------------------------------------------------------------------
    // CLIENT LOANS & REPAYMENTS SCHEDULE
    // --------------------------------------------------------------------------
    async function loadMyLoans() {
      const container = document.getElementById('myLoansListContainer');
      try {
        const res = await fetch('/api/loans/my-loans', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const loans = await res.json();
        if (!loans || loans.length === 0) {
          container.innerHTML = '<div style="text-align: center; color: #9CA3AF; padding: 30px;">No loans found.</div>';
          return;
        }
        container.innerHTML = loans.map(l => `
          <div class="breakdown-card">
            <div style="display: flex; justify-content: space-between; font-weight: 800; margin-bottom: 4px;">
              <span>Ref: ${l.loan_reference}</span>
              <span style="color: var(--primary-green);">R${l.amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</span>
            </div>
            <div style="font-size: 12px; color: #64748B;">Total Repayable (30%): R${l.total_repayable.toLocaleString('en-ZA', { minimumFractionDigits: 2 })} &bull; Due: ${l.first_payment_due}</div>
            <div style="font-size: 11px; font-weight: 800; margin-top: 6px; text-transform: uppercase;">Status: ${l.status}</div>
          </div>
        `).join('');
      } catch (e) {
        container.innerHTML = '<div style="color: #EF4444;">Error loading loans.</div>';
      }
    }

    async function loadRepaymentsSchedule() {
      const container = document.getElementById('repaymentsListContainer');
      try {
        const res = await fetch('/api/loans/my-repayments', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const reps = await res.json();
        if (!reps || reps.length === 0) {
          container.innerHTML = '<div style="text-align: center; color: #9CA3AF; padding: 30px;">No upcoming payments scheduled.</div>';
          return;
        }
        container.innerHTML = reps.map(r => `
          <div class="breakdown-card">
            <div style="display: flex; justify-content: space-between; font-weight: 800;">
              <span>Due: ${r.due_date}</span>
              <span style="color: var(--primary-green);">R${r.amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</span>
            </div>
            <div style="font-size: 12px; color: #64748B;">Status: ${r.status} ${r.paid_at ? `&bull; Paid: ${r.paid_at}` : ''}</div>
          </div>
        `).join('');
      } catch (e) {
        container.innerHTML = '<div style="color: #EF4444;">Error loading payments.</div>';
      }
    }

    // Modal Helpers
    function openNotificationsModal() {
      openModal('notifModal');
      loadNotificationsList();
    }
    async function loadNotificationsList() {
      const container = document.getElementById('notifListContainer');
      try {
        const res = await fetch('/api/loans/notifications', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const notifs = await res.json();
        if (!notifs || notifs.length === 0) {
          container.innerHTML = '<div style="text-align: center; color: #9CA3AF; padding: 20px;">No notifications.</div>';
          return;
        }
        container.innerHTML = notifs.map(n => `
          <div style="background: ${n.is_read ? '#F9FAFB' : '#F0FDF4'}; border: 1px solid ${n.is_read ? '#E5E7EB' : '#BBF7D0'}; padding: 12px; border-radius: 10px;">
            <div style="font-weight: 800; font-size: 13px; color: #111827;">${n.title}</div>
            <div style="font-size: 12px; color: #4B5563; margin-top: 2px;">${n.message}</div>
          </div>
        `).join('');
      } catch (e) {}
    }
    async function markAllNotificationsRead() {
      try {
        await fetch('/api/loans/notifications/mark-read', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        document.getElementById('homeNotifDot').style.display = 'none';
        loadNotificationsList();
      } catch (e) {}
    }

    function openShareAppModal() {
      openModal('shareAppModal');
      drawSimpleQrCode();
    }
    function handleNativeShare() {
      if (navigator.share) {
        navigator.share({ title: 'HH Cash Solutions', text: SHARE_MESSAGE, url: window.location.origin });
      } else {
        copyAppUrl();
      }
    }
    function shareToWhatsApp() {
      window.open(`https://wa.me/?text=${encodeURIComponent(SHARE_MESSAGE)}`, '_blank');
    }
    function copyAppUrl() {
      navigator.clipboard.writeText(window.location.origin);
      showToast('App URL copied to clipboard!', '📋');
    }
    function drawSimpleQrCode() {
      const canvas = document.getElementById('qrCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, 160, 160);
      ctx.fillStyle = '#0B7A28';
      ctx.fillRect(20, 20, 40, 40);
      ctx.fillRect(100, 20, 40, 40);
      ctx.fillRect(20, 100, 40, 40);
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(28, 28, 24, 24);
      ctx.fillRect(108, 28, 24, 24);
      ctx.fillRect(28, 108, 24, 24);
      ctx.fillStyle = '#0B7A28';
      ctx.fillRect(34, 34, 12, 12);
      ctx.fillRect(114, 34, 12, 12);
      ctx.fillRect(34, 114, 12, 12);
      ctx.fillRect(75, 25, 10, 110);
      ctx.fillRect(25, 75, 110, 10);
    }

    function openSupportModal() { openModal('supportModal'); }
    function openForgotPasswordModal() { openModal('forgotModal'); }
    function contactSupportWhatsApp(topic) {
      const text = encodeURIComponent(`Hi HH Cash Solutions, inquiry regarding: ${topic}`);
      window.open(`https://wa.me/27821234567?text=${text}`, '_blank');
    }

    // App Init
    window.addEventListener('DOMContentLoaded', () => {
      setTimeout(() => {
        const splash = document.getElementById('splashScreen');
        if (splash) {
          splash.style.opacity = '0';
          setTimeout(() => {
            splash.style.display = 'none';
            if (authToken) {
              loadUserProfile();
              navigateToScreen('homeScreen');
            } else {
              navigateToScreen('loginScreen');
            }
          }, 350);
        }
      }, 2200);
    });
  </script>
</body>
</html>
'''

with open("ui/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"ui/index.html written successfully! Size: {len(html_content)} bytes")
