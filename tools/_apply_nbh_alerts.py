"""Apply neighbourhood alert feature patches to CivicRadar."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "js" / "app.js"
app = APP.read_text(encoding="utf-8")

# --- 1. Constants ---
CONST_OLD = "  const REPORT_REMINDER_DAYS = 2;\n\n  // Location-aware in-app nudge"
CONST_NEW = """  const REPORT_REMINDER_DAYS = 2;

  // Neighbourhood new-report + resolved FYI alerts (Profile opt-in; rate-limited).
  const NBH_ALERT_NEW_KEY = 'civicradar_nbh_alert_new';
  const NBH_ALERT_RESOLVED_KEY = 'civicradar_nbh_alert_resolved';
  const NBH_ALERT_LOG_KEY = 'civicradar_nbh_alert_log';
  const NBH_ALERT_NEW_SEEN_KEY = 'civicradar_nbh_new_seen';
  const NBH_ALERT_RESOLVED_SEEN_KEY = 'civicradar_nbh_resolved_seen';
  const NBH_ALERT_RESOLVE_DIGEST_KEY = 'civicradar_nbh_resolve_digest';
  const NBH_ALERT_MIN_GAP_MS = 5 * 60 * 1000;
  const NBH_ALERT_MAX_PER_24H = 3;
  const NBH_ALERT_DIGEST_MS = 60 * 60 * 1000;

  // Location-aware in-app nudge"""

if CONST_OLD not in app:
    raise SystemExit("constants anchor missing")
app = app.replace(CONST_OLD, CONST_NEW, 1)

# --- 2. Version bump ---
app = app.replace("const CIVIC_APP_VERSION = 'v96';", "const CIVIC_APP_VERSION = 'v97';", 1)

# --- 3. i18n EN ---
I18N_EN_OLD = "      'settings.reminder.denied': 'Notifications are blocked — we\\'ll show a gentle in-app reminder instead.',\n\n      'notify.report.title':"
I18N_EN_NEW = """      'settings.reminder.denied': 'Notifications are blocked — we\\'ll show a gentle in-app reminder instead.',

      'settings.nbh.title': 'Neighbourhood updates',
      'settings.nbh.sub': 'When neighbours in your society report or resolve hazards.',
      'settings.nbh.new.label': 'New reports nearby',
      'settings.nbh.new.sub': 'Nudge when someone pins a hazard in your society or ward.',
      'settings.nbh.resolved.label': 'Resolved nearby',
      'settings.nbh.resolved.sub': 'Good news when a hazard near you is marked resolved.',
      'settings.nbh.on': 'Neighbourhood updates on.',
      'settings.nbh.newOff': 'New report alerts off.',
      'settings.nbh.resolvedOff': 'Resolved updates off.',
      'settings.nbh.denied': 'Notifications blocked — we\\'ll show updates in the app instead.',
      'notify.nbh.new.title': 'New report near you',
      'notify.nbh.new.body': 'New report near {society}: {hazard} — open map to Me too',
      'notify.nbh.new.cta': 'View on map',
      'notify.nbh.resolved.title': 'Good news nearby',
      'notify.nbh.resolved.body': '{hazard} near {society} was marked resolved',
      'notify.nbh.resolved.bodyMany': '{n} hazards near {society} were marked resolved',
      'notify.nbh.resolved.cta': 'View on map',

      'notify.report.title':"""

if I18N_EN_OLD not in app:
    raise SystemExit("i18n en anchor missing")
app = app.replace(I18N_EN_OLD, I18N_EN_NEW, 1)

# --- i18n HI ---
I18N_HI_OLD = "      'settings.reminder.denied': 'सूचनाएँ ब्लॉक हैं — हम इसके बजाय ऐप में हल्की याद दिखाएँगे।',\n\n      'notify.report.title':"
I18N_HI_NEW = """      'settings.reminder.denied': 'सूचनाएँ ब्लॉक हैं — हम इसके बजाय ऐप में हल्की याद दिखाएँगे।',

      'settings.nbh.title': 'पड़ोस अपडेट',
      'settings.nbh.sub': 'जब पड़ोसी आपकी सोसाइटी में जोखिम रिपोर्ट या हल करें।',
      'settings.nbh.new.label': 'पास में नई रिपोर्ट',
      'settings.nbh.new.sub': 'आपके पड़ोस/वार्ड में कोई पिन करे तो याद।',
      'settings.nbh.resolved.label': 'पास में हल',
      'settings.nbh.resolved.sub': 'पास का जोखिम हल हो तो खुशखबरी।',
      'settings.nbh.on': 'पड़ोस अपडेट चालू।',
      'settings.nbh.newOff': 'नई रिपोर्ट अलर्ट बंद।',
      'settings.nbh.resolvedOff': 'हल अपडेट बंद।',
      'settings.nbh.denied': 'सूचनाएँ ब्लॉक — अपडेट ऐप में दिखेंगे।',
      'notify.nbh.new.title': 'पास में नई रिपोर्ट',
      'notify.nbh.new.body': '{society} के पास: {hazard} — नक्शे पर Me too',
      'notify.nbh.new.cta': 'नक्शा देखें',
      'notify.nbh.resolved.title': 'पास की खुशखबरी',
      'notify.nbh.resolved.body': '{society} के पास {hazard} हल चिह्नित',
      'notify.nbh.resolved.bodyMany': '{society} के पास {n} जोखिम हल',
      'notify.nbh.resolved.cta': 'नक्शा देखें',

      'notify.report.title':"""
app = app.replace(I18N_HI_OLD, I18N_HI_NEW, 1)

# --- i18n MR ---
I18N_MR_OLD = "      'settings.reminder.denied': 'सूचना ब्लॉक आहेत — त्याऐवजी आम्ही अॅपमध्ये सौम्य आठवण दाखवू.',\n\n      'notify.report.title':"
I18N_MR_NEW = """      'settings.reminder.denied': 'सूचना ब्लॉक आहेत — त्याऐवजी आम्ही अॅपमध्ये सौम्य आठवण दाखवू.',

      'settings.nbh.title': 'Neighbourhood अपडेट',
      'settings.nbh.sub': 'शेजारी तुमच्या society मध्ये hazard report किंवा resolve करतील तेव्हा.',
      'settings.nbh.new.label': 'जवळच्या नवीन reports',
      'settings.nbh.new.sub': 'तुमच्या society/ward मध्ये pin झाल्यावर सूचना.',
      'settings.nbh.resolved.label': 'जवळ resolve',
      'settings.nbh.resolved.sub': 'जवळचा hazard resolve झाल्यावर good news.',
      'settings.nbh.on': 'Neighbourhood अपडेट सुरू.',
      'settings.nbh.newOff': 'नवीन report alerts बंद.',
      'settings.nbh.resolvedOff': 'Resolve अपडेट बंद.',
      'settings.nbh.denied': 'सूचना ब्लॉक — अपडेट अॅपमध्ये.',
      'notify.nbh.new.title': 'जवळ नवीन report',
      'notify.nbh.new.body': '{society} जवळ: {hazard} — map वर Me too',
      'notify.nbh.new.cta': 'Map पहा',
      'notify.nbh.resolved.title': 'जवळची good news',
      'notify.nbh.resolved.body': '{society} जवळ {hazard} resolve',
      'notify.nbh.resolved.bodyMany': '{society} जवळ {n} hazards resolve',
      'notify.nbh.resolved.cta': 'Map पहा',

      'notify.report.title':"""
app = app.replace(I18N_MR_OLD, I18N_MR_NEW, 1)

# --- i18n GU ---
I18N_GU_OLD = "      'settings.reminder.denied': 'સૂચનાઓ બ્લોક છે — તેના બદલે અમે એપમાં હળવી યાદ બતાવીશું.',\n\n      'notify.report.title':"
I18N_GU_NEW = """      'settings.reminder.denied': 'સૂચનાઓ બ્લોક છે — તેના બદલે અમે એપમાં હળવી યાદ બતાવીશું.',

      'settings.nbh.title': 'Neighbourhood અપડેટ',
      'settings.nbh.sub': 'પડોશીઓ તમારી society માં hazard report અથવા resolve કરે ત્યારે.',
      'settings.nbh.new.label': 'નજીકની નવી reports',
      'settings.nbh.new.sub': 'તમારી society/ward માં pin થાય ત્યારે યાદ.',
      'settings.nbh.resolved.label': 'નજીક resolve',
      'settings.nbh.resolved.sub': 'નજીકનો hazard resolve થાય ત્યારે good news.',
      'settings.nbh.on': 'Neighbourhood અપડેટ ચાલુ.',
      'settings.nbh.newOff': 'નવી report alerts બંધ.',
      'settings.nbh.resolvedOff': 'Resolve અપડેટ બંધ.',
      'settings.nbh.denied': 'સૂચનાઓ બ્લોક — અપડેટ એપમાં.',
      'notify.nbh.new.title': 'નજીક નવી report',
      'notify.nbh.new.body': '{society} નજીક: {hazard} — map પર Me too',
      'notify.nbh.new.cta': 'Map જુઓ',
      'notify.nbh.resolved.title': 'નજીકની good news',
      'notify.nbh.resolved.body': '{society} નજીક {hazard} resolve',
      'notify.nbh.resolved.bodyMany': '{society} નજીક {n} hazards resolve',
      'notify.nbh.resolved.cta': 'Map જુઓ',

      'notify.report.title':"""
app = app.replace(I18N_GU_OLD, I18N_GU_NEW, 1)

NBH_MODULE = r'''
  /* ---------- Neighbourhood alerts (new report + resolved FYI) ----------
     Matching: same city + ward + normalized society when report has society;
     ward-only fallback when report has no society. Default ON when profile society set.
     Shared rate limit: max 3 alerts / 24h, min 5 min gap. Resolved batched per hour. */

  let nbhResolveDigestTimer = null;

  function defaultNbhAlertsOn() {
    return !!(user.society && String(user.society).trim());
  }

  function isNbhNewAlertsEnabled() {
    const v = localStorage.getItem(NBH_ALERT_NEW_KEY);
    if (v === '0') return false;
    if (v === '1') return true;
    return defaultNbhAlertsOn();
  }

  function isNbhResolvedAlertsEnabled() {
    const v = localStorage.getItem(NBH_ALERT_RESOLVED_KEY);
    if (v === '0') return false;
    if (v === '1') return true;
    return defaultNbhAlertsOn();
  }

  function setNbhNewAlertsEnabled(enabled) {
    try { localStorage.setItem(NBH_ALERT_NEW_KEY, enabled ? '1' : '0'); } catch {}
    if (Backend.enabled) Backend.updateNotificationPrefs({ newAlerts: enabled });
    if (window.CivicAnalytics) CivicAnalytics.track('nbh_alert_optin', { type: 'new', enabled: !!enabled }, user.ward);
  }

  function setNbhResolvedAlertsEnabled(enabled) {
    try { localStorage.setItem(NBH_ALERT_RESOLVED_KEY, enabled ? '1' : '0'); } catch {}
    if (Backend.enabled) Backend.updateNotificationPrefs({ resolvedAlerts: enabled });
    if (window.CivicAnalytics) CivicAnalytics.track('nbh_alert_optin', { type: 'resolved', enabled: !!enabled }, user.ward);
  }

  function syncNbhAlertToggles() {
    const n = $('#nbhNewAlertToggle');
    const r = $('#nbhResolvedAlertToggle');
    if (n) n.checked = isNbhNewAlertsEnabled();
    if (r) r.checked = isNbhResolvedAlertsEnabled();
  }

  function handleNbhNewAlertToggle(enabled) {
    setNbhNewAlertsEnabled(enabled);
    if (!enabled) { showToast(t('settings.nbh.newOff'), 'info', 2600); return; }
    requestNotificationForNbhToggle(true);
  }

  function handleNbhResolvedAlertToggle(enabled) {
    setNbhResolvedAlertsEnabled(enabled);
    if (!enabled) { showToast(t('settings.nbh.resolvedOff'), 'info', 2600); return; }
    requestNotificationForNbhToggle(true);
  }

  function requestNotificationForNbhToggle(showOnToast) {
    if (!notificationsSupported()) {
      if (showOnToast) showToast(t('settings.nbh.denied'), 'info', 4200);
      return;
    }
    let perm = 'default';
    try { perm = Notification.permission; } catch {}
    if (perm === 'granted') {
      if (showOnToast) showToast(t('settings.nbh.on'), 'success', 3600);
      return;
    }
    if (perm === 'denied') {
      showToast(t('settings.nbh.denied'), 'info', 4200);
      return;
    }
    try {
      const req = Notification.requestPermission();
      if (req && typeof req.then === 'function') {
        req.then((result) => {
          showToast(
            result === 'granted' ? t('settings.nbh.on') : t('settings.nbh.denied'),
            result === 'granted' ? 'success' : 'info',
            result === 'granted' ? 3600 : 4200
          );
        }).catch(() => { if (showOnToast) showToast(t('settings.nbh.on'), 'success', 3600); });
      } else if (showOnToast) showToast(t('settings.nbh.on'), 'success', 3600);
    } catch {
      if (showOnToast) showToast(t('settings.nbh.on'), 'success', 3600);
    }
  }

  function normalizeNbhToken(s) {
    return String(s || '').trim().toLowerCase().replace(/\s+/g, ' ');
  }

  function nbhSocietyLabel(report) {
    const soc = (report && (report.society || report.neighbourhood)) || user.society || '';
    const trimmed = String(soc).trim();
    if (trimmed) return trimmed;
    return wardLabelShort((report && report.ward) || user.ward || '');
  }

  function reportMatchesUserNeighbourhood(report) {
    if (!user.ward || !user.tosAccepted) return false;
    if (isAdmin || isLead) return false;
    const city = report.city || getReportCity(report);
    if (city !== getUserCity()) return false;
    if ((report.ward || '') !== user.ward) return false;
    const reportSoc = normalizeNbhToken(report.society || report.neighbourhood);
    const userSoc = normalizeNbhToken(user.society);
    if (reportSoc && userSoc) return reportSoc === userSoc;
    if (!reportSoc) return true;
    return false;
  }

  function loadNbhAlertLog() {
    try {
      const raw = localStorage.getItem(NBH_ALERT_LOG_KEY);
      const parsed = raw ? JSON.parse(raw) : { timestamps: [] };
      if (!Array.isArray(parsed.timestamps)) parsed.timestamps = [];
      return parsed;
    } catch {
      return { timestamps: [] };
    }
  }

  function saveNbhAlertLog(log) {
    try { localStorage.setItem(NBH_ALERT_LOG_KEY, JSON.stringify(log)); } catch {}
  }

  function canSendNbhAlert() {
    const log = loadNbhAlertLog();
    const now = Date.now();
    const recent = (log.timestamps || []).filter((ts) => now - ts < 86400000);
    if (recent.length >= NBH_ALERT_MAX_PER_24H) return false;
    const last = recent.length ? Math.max(...recent) : 0;
    if (last && now - last < NBH_ALERT_MIN_GAP_MS) return false;
    return true;
  }

  function recordNbhAlertSent() {
    const log = loadNbhAlertLog();
    const now = Date.now();
    log.timestamps = (log.timestamps || []).filter((ts) => now - ts < 86400000);
    log.timestamps.push(now);
    saveNbhAlertLog(log);
  }

  function loadNbhIdSet(key) {
    try {
      const raw = localStorage.getItem(key);
      const arr = raw ? JSON.parse(raw) : [];
      return new Set(Array.isArray(arr) ? arr.map(String) : []);
    } catch {
      return new Set();
    }
  }

  function saveNbhIdSet(key, set) {
    try { localStorage.setItem(key, JSON.stringify([...set].slice(-500))); } catch {}
  }

  function loadResolveDigest() {
    try {
      return JSON.parse(localStorage.getItem(NBH_ALERT_RESOLVE_DIGEST_KEY) || 'null') || {};
    } catch {
      return {};
    }
  }

  function saveResolveDigest(d) {
    try { localStorage.setItem(NBH_ALERT_RESOLVE_DIGEST_KEY, JSON.stringify(d)); } catch {}
  }

  function focusReportOnMap(reportId) {
    const r = findReportById(reportId);
    if (!r) return;
    closeAllModals();
    if (r.lat != null && r.lng != null && map) {
      map.setView([r.lat, r.lng], 16);
      const marker = reportMarkerMap.get(String(reportId));
      if (marker) marker.openPopup();
    }
  }

  function showNbhAlertInApp(title, body, reportId, ctaKey) {
    window.__civicNbhAlertLast = body;
    showToast(body, 'info', 9000, {
      label: t(ctaKey || 'notify.nbh.new.cta'),
      onClick: () => focusReportOnMap(reportId),
    });
  }

  function fireNbhAlertNotification(title, body, reportId, alertType) {
    const tag = `civicradar-nbh-${alertType}`;
    const opts = {
      body,
      tag,
      icon: 'assets/icon-192.png',
      badge: 'assets/favicon-32.png',
      data: { reportId: String(reportId || ''), type: alertType, url: reportId ? `?report=${reportId}` : './' },
    };
    try {
      if (navigator.serviceWorker && navigator.serviceWorker.ready) {
        navigator.serviceWorker.ready
          .then((reg) => {
            if (reg && reg.showNotification) reg.showNotification(title, opts);
            else throw new Error('no showNotification');
          })
          .catch(() => { try { new Notification(title, opts); } catch { showNbhAlertInApp(title, body, reportId, alertType === 'resolved' ? 'notify.nbh.resolved.cta' : 'notify.nbh.new.cta'); } });
        return true;
      }
      new Notification(title, opts);
      return true;
    } catch {
      return false;
    }
  }

  function deliverNbhAlert(kind, report, bodyOverride) {
    if (!report || !reportMatchesUserNeighbourhood(report)) return false;
    if (report.reporterId === user.id) return false;
    if (!canSendNbhAlert()) return false;
    const society = nbhSocietyLabel(report);
    const hazard = hazardLabel(report.hazard);
    const isResolved = kind === 'resolved';
    const title = t(isResolved ? 'notify.nbh.resolved.title' : 'notify.nbh.new.title');
    const body = bodyOverride || (isResolved
      ? t('notify.nbh.resolved.body').replace('{society}', society).replace('{hazard}', hazard)
      : t('notify.nbh.new.body').replace('{society}', society).replace('{hazard}', hazard));
    window.__civicNbhAlertLast = body;
    recordNbhAlertSent();
    if (window.CivicAnalytics) CivicAnalytics.track(isResolved ? 'nbh_alert_resolved' : 'nbh_alert_new', { reportId: String(report.id) }, user.ward);
    let perm = 'default';
    if (notificationsSupported()) { try { perm = Notification.permission; } catch {} }
    if (perm === 'granted' && fireNbhAlertNotification(title, body, report.id, kind)) return true;
    showNbhAlertInApp(title, body, report.id, isResolved ? 'notify.nbh.resolved.cta' : 'notify.nbh.new.cta');
    return true;
  }

  function maybeDeliverNbhNewReportAlert(report) {
    if (!isNbhNewAlertsEnabled()) return;
    if (!report || report.status === 'resolved') return;
    deliverNbhAlert('new', report);
  }

  function queueNbhResolvedAlert(report) {
    if (!isNbhResolvedAlertsEnabled()) return;
    if (!report || report.status !== 'resolved') return;
    const hourKey = Math.floor(Date.now() / NBH_ALERT_DIGEST_MS);
    const digest = loadResolveDigest();
    if (digest.hourKey !== hourKey) {
      digest.hourKey = hourKey;
      digest.count = 0;
      digest.society = nbhSocietyLabel(report);
      digest.lastReportId = report.id;
    }
    digest.count = (digest.count || 0) + 1;
    digest.lastReportId = report.id;
    saveResolveDigest(digest);
    clearTimeout(nbhResolveDigestTimer);
    nbhResolveDigestTimer = setTimeout(flushNbhResolveDigest, 400);
  }

  function flushNbhResolveDigest() {
    nbhResolveDigestTimer = null;
    const digest = loadResolveDigest();
    if (!digest.count || !digest.lastReportId) return;
    const report = findReportById(digest.lastReportId) || { id: digest.lastReportId, ward: user.ward, city: getUserCity(), society: digest.society, status: 'resolved', hazard: 'stagnant-water' };
    let body;
    if (digest.count > 1) {
      body = t('notify.nbh.resolved.bodyMany').replace('{n}', String(digest.count)).replace('{society}', digest.society || nbhSocietyLabel(report));
    }
    deliverNbhAlert('resolved', report, body);
    saveResolveDigest({});
  }

  function maybeDeliverNbhResolvedAlert(report) {
    queueNbhResolvedAlert(report);
  }

  function fanOutLocalNbhNewReport(report) {
    if (!report) return;
    try {
      const q = JSON.parse(localStorage.getItem('civicradar_nbh_local_queue') || '[]');
      q.push({ type: 'new', report: { id: report.id, hazard: report.hazard, society: report.society, ward: report.ward, city: report.city, reporterId: report.reporterId, status: report.status }, at: Date.now() });
      localStorage.setItem('civicradar_nbh_local_queue', JSON.stringify(q.slice(-50)));
    } catch {}
    processLocalNbhQueue();
  }

  function fanOutLocalNbhResolved(report) {
    if (!report) return;
    try {
      const q = JSON.parse(localStorage.getItem('civicradar_nbh_local_queue') || '[]');
      q.push({ type: 'resolved', report: { id: report.id, hazard: report.hazard, society: report.society, ward: report.ward, city: report.city, reporterId: report.reporterId, status: 'resolved' }, at: Date.now() });
      localStorage.setItem('civicradar_nbh_local_queue', JSON.stringify(q.slice(-50)));
    } catch {}
    processLocalNbhQueue();
  }

  function processLocalNbhQueue() {
    let q;
    try { q = JSON.parse(localStorage.getItem('civicradar_nbh_local_queue') || '[]'); } catch { return; }
    if (!q.length) return;
    const remaining = [];
    q.forEach((item) => {
      const r = item.report;
      if (!r || r.reporterId === user.id) return;
      if (item.type === 'new' && isNbhNewAlertsEnabled()) {
        if (!deliverNbhAlert('new', r)) remaining.push(item);
      } else if (item.type === 'resolved' && isNbhResolvedAlertsEnabled()) {
        queueNbhResolvedAlert(r);
      } else {
        remaining.push(item);
      }
    });
    try { localStorage.setItem('civicradar_nbh_local_queue', JSON.stringify(remaining)); } catch {}
  }

  function processNeighbourhoodAlertsOnSync(prevReports) {
    if (!user.ward || isAdmin || isLead) return;
    const prevMap = new Map((prevReports || []).map((r) => [String(r.id), r]));
    const newSeen = loadNbhIdSet(NBH_ALERT_NEW_SEEN_KEY);
    const resolvedSeen = loadNbhIdSet(NBH_ALERT_RESOLVED_SEEN_KEY);
    loadReports().forEach((r) => {
      if (r.reporterId === user.id) return;
      if (!reportMatchesUserNeighbourhood(r)) return;
      const prev = prevMap.get(String(r.id));
      if (r.status !== 'resolved' && !newSeen.has(String(r.id)) && isNbhNewAlertsEnabled()) {
        if (deliverNbhAlert('new', r)) newSeen.add(String(r.id));
      }
      if (r.status === 'resolved' && !resolvedSeen.has(String(r.id))) {
        const wasPending = !prev || prev.status !== 'resolved';
        if (wasPending && isNbhResolvedAlertsEnabled()) {
          queueNbhResolvedAlert(r);
          resolvedSeen.add(String(r.id));
        }
      }
    });
    saveNbhIdSet(NBH_ALERT_NEW_SEEN_KEY, newSeen);
    saveNbhIdSet(NBH_ALERT_RESOLVED_SEEN_KEY, resolvedSeen);
  }

  function applyNbhPrefsFromProfile(profile) {
    if (!profile) return;
    if (profile.neighbourhood_new_alerts_enabled === true) localStorage.setItem(NBH_ALERT_NEW_KEY, '1');
    else if (profile.neighbourhood_new_alerts_enabled === false) localStorage.setItem(NBH_ALERT_NEW_KEY, '0');
    if (profile.neighbourhood_resolved_alerts_enabled === true) localStorage.setItem(NBH_ALERT_RESOLVED_KEY, '1');
    else if (profile.neighbourhood_resolved_alerts_enabled === false) localStorage.setItem(NBH_ALERT_RESOLVED_KEY, '0');
    syncNbhAlertToggles();
  }

  window.__civicSimulateNbhNewReport = function (report) {
    const r = report || { id: 'sim-nbh-new', hazard: 'stagnant-water', society: user.society, ward: user.ward, city: getUserCity(), reporterId: 'other-user', status: 'pending' };
    maybeDeliverNbhNewReportAlert(r);
  };
  window.__civicSimulateNbhResolved = function (report) {
    const r = report || { id: 'sim-nbh-res', hazard: 'stagnant-water', society: user.society, ward: user.ward, city: getUserCity(), reporterId: 'other-user', status: 'resolved' };
    maybeDeliverNbhResolvedAlert(r);
  };
  window.__civicResetNbhAlertLimits = function () {
    localStorage.removeItem(NBH_ALERT_LOG_KEY);
    localStorage.removeItem(NBH_ALERT_RESOLVE_DIGEST_KEY);
    clearTimeout(nbhResolveDigestTimer);
    nbhResolveDigestTimer = null;
  };
  window.processLocalNbhQueue = processLocalNbhQueue;
  window.syncNbhAlertToggles = syncNbhAlertToggles;

'''

ANCHOR = "  window.maybeShowReportReminder = maybeShowReportReminder;\n\n\n\n  /* ---------- Location-aware in-app nudge"
if ANCHOR not in app:
    raise SystemExit("nbh module anchor missing")
app = app.replace(ANCHOR, "  window.maybeShowReportReminder = maybeShowReportReminder;\n" + NBH_MODULE + "\n  /* ---------- Location-aware in-app nudge", 1)

# Hook submitReport fan-out
SUBMIT_OLD = "        Backend.insertReport(report);\n\n        if (window.CivicAnalytics) {"
SUBMIT_NEW = """        Backend.insertReport(report);

        fanOutLocalNbhNewReport(report);

        if (window.CivicAnalytics) {"""
if SUBMIT_OLD not in app:
    raise SystemExit("submitReport hook missing")
app = app.replace(SUBMIT_OLD, SUBMIT_NEW, 1)

# Hook applyResolution
RES_OLD = """    Backend.updateReportResolution(

      reportId, 'resolved', by, resolvedAt,

      resolutionImage || reports[idx].resolutionImage,

      src,

      reports[idx].communityVerifiedAt || null

    );

    if (window.CivicAnalytics) {"""
RES_NEW = RES_OLD.replace(
    "    );\n\n    if (window.CivicAnalytics) {",
    "    );\n\n    fanOutLocalNbhResolved(reports[idx]);\n\n    if (window.CivicAnalytics) {",
    1,
)
if RES_OLD not in app:
    raise SystemExit("applyResolution hook missing")
app = app.replace(RES_OLD, RES_NEW, 1)

# refreshAllViews hook
REF_OLD = "      processSyncReminders();\n\n    } catch (e) {"
REF_NEW = "      processSyncReminders();\n\n      processLocalNbhQueue();\n\n    } catch (e) {"
if REF_OLD not in app:
    raise SystemExit("refreshAllViews hook missing")
app = app.replace(REF_OLD, REF_NEW, 1)

# pullAll hook - find saveReports after merge
PULL_OLD = """        saveReports(merged);
      }
      if (pls) {"""
PULL_NEW = """        const prevReports = loadReports();
        saveReports(merged);
        processNeighbourhoodAlertsOnSync(prevReports);
      }
      if (pls) {"""
if PULL_OLD not in app:
    raise SystemExit("pullAll hook missing")
app = app.replace(PULL_OLD, PULL_NEW, 1)

# Backend getMyRole + updateNotificationPrefs
GMR_OLD = "      const { data, error } = await this.client.from('profiles').select('role, ward, city, coordinator_scope, neighbourhood_label').eq('id', u.id).single();"
GMR_NEW = "      const { data, error } = await this.client.from('profiles').select('role, ward, city, coordinator_scope, neighbourhood_label, society, neighbourhood_new_alerts_enabled, neighbourhood_resolved_alerts_enabled').eq('id', u.id).single();"
app = app.replace(GMR_OLD, GMR_NEW, 1)

BACKEND_INSERT = """
    async updateNotificationPrefs({ newAlerts, resolvedAlerts }) {
      if (!this.enabled || !this.client) return;
      const patch = {};
      if (typeof newAlerts === 'boolean') patch.neighbourhood_new_alerts_enabled = newAlerts;
      if (typeof resolvedAlerts === 'boolean') patch.neighbourhood_resolved_alerts_enabled = resolvedAlerts;
      if (!Object.keys(patch).length) return;
      const { error } = await this.client.from('profiles').update(patch).eq('id', user.id);
      if (error) console.warn('Notification prefs sync failed:', error.message);
    },

"""
BACKEND_ANCHOR = "    async signOut() {"
if BACKEND_INSERT.strip() not in app:
    if BACKEND_ANCHOR not in app:
        raise SystemExit("Backend signOut anchor missing")
    app = app.replace(BACKEND_ANCHOR, BACKEND_INSERT + "    async signOut() {", 1)

# restoreElevatedRole / profile load - apply prefs after getMyRole
REST_OLD = """        user.neighbourhoodLabel = profile.neighbourhood_label || '';

        saveUser();"""
REST_NEW = REST_OLD + "\n\n        applyNbhPrefsFromProfile(profile);"
if REST_OLD in app and "applyNbhPrefsFromProfile" not in app.split(REST_OLD)[1][:200]:
    app = app.replace(REST_OLD, REST_NEW, 1)

# wipeLocalUserData keys
WIPE_OLD = "      LOCBANNER_SNOOZE_KEY,\n\n    ].forEach"
WIPE_NEW = "      LOCBANNER_SNOOZE_KEY,\n\n      NBH_ALERT_NEW_KEY, NBH_ALERT_RESOLVED_KEY, NBH_ALERT_LOG_KEY,\n\n      NBH_ALERT_NEW_SEEN_KEY, NBH_ALERT_RESOLVED_SEEN_KEY, NBH_ALERT_RESOLVE_DIGEST_KEY,\n\n    ].forEach"
app = app.replace(WIPE_OLD, WIPE_NEW, 1)

# Event listeners for toggles
TOG_OLD = """    const reportReminderToggle = $('#reportReminderToggle');

    if (reportReminderToggle) {

      reportReminderToggle.addEventListener('change', (e) => {

        handleReportReminderToggle(e.target.checked);

      });

    }"""
TOG_NEW = TOG_OLD + """



    const nbhNewAlertToggle = $('#nbhNewAlertToggle');

    if (nbhNewAlertToggle) {

      nbhNewAlertToggle.addEventListener('change', (e) => {

        handleNbhNewAlertToggle(e.target.checked);

      });

    }



    const nbhResolvedAlertToggle = $('#nbhResolvedAlertToggle');

    if (nbhResolvedAlertToggle) {

      nbhResolvedAlertToggle.addEventListener('change', (e) => {

        handleNbhResolvedAlertToggle(e.target.checked);

      });

    }"""
if TOG_OLD not in app:
    raise SystemExit("toggle listener anchor missing")
app = app.replace(TOG_OLD, TOG_NEW, 1)

# sync toggles on profile open - find syncReportReminderToggle call
SYNC_OLD = "    syncReportReminderToggle();"
SYNC_NEW = "    syncReportReminderToggle();\n\n    syncNbhAlertToggles();"
if app.count("syncNbhAlertToggles();") < 2:
    app = app.replace(SYNC_OLD, SYNC_NEW, 1)

# SW message listener in registerServiceWorker
SW_OLD = """  function registerServiceWorker() {

    if ('serviceWorker' in navigator) {

      navigator.serviceWorker.register('sw.js').catch(() => {});

    }

  }"""
SW_NEW = """  function registerServiceWorker() {

    if ('serviceWorker' in navigator) {

      navigator.serviceWorker.register('sw.js').catch(() => {});

      navigator.serviceWorker.addEventListener('message', (ev) => {

        if (ev.data && ev.data.type === 'nbh-alert-focus') focusReportOnMap(ev.data.reportId);

      });

    }

  }"""
app = app.replace(SW_OLD, SW_NEW, 1)

# Backend.init end - process queue on load
INIT_OLD = "  Backend.init().then(() => handleReportDeepLink());"
INIT_NEW = "  Backend.init().then(() => { handleReportDeepLink(); processLocalNbhQueue(); });"
app = app.replace(INIT_OLD, INIT_NEW, 1)

APP.write_text(app, encoding="utf-8")
print("app.js neighbourhood alerts applied")

# index.html
IDX = ROOT / "index.html"
idx = IDX.read_text(encoding="utf-8")
NBH_HTML = """
        <label class="toggle-row" for="nbhNewAlertToggle">
          <span class="toggle-row__text">
            <span class="toggle-row__label" data-i18n="settings.nbh.new.label">New reports nearby</span>
            <span class="toggle-row__sub" data-i18n="settings.nbh.new.sub">Nudge when someone pins a hazard in your society or ward.</span>
          </span>
          <input type="checkbox" id="nbhNewAlertToggle" class="toggle-row__input">
          <span class="toggle-row__switch" aria-hidden="true"></span>
        </label>
        <label class="toggle-row" for="nbhResolvedAlertToggle">
          <span class="toggle-row__text">
            <span class="toggle-row__label" data-i18n="settings.nbh.resolved.label">Resolved nearby</span>
            <span class="toggle-row__sub" data-i18n="settings.nbh.resolved.sub">Good news when a hazard near you is marked resolved.</span>
          </span>
          <input type="checkbox" id="nbhResolvedAlertToggle" class="toggle-row__input">
          <span class="toggle-row__switch" aria-hidden="true"></span>
        </label>
"""
IDX_ANCHOR = '      <h3 class="section-title" data-i18n="settings.title">Reminders</h3>'
if 'nbhNewAlertToggle' not in idx:
    idx = idx.replace(
        IDX_ANCHOR,
        '      <h3 class="section-title" data-i18n="settings.nbh.title">Neighbourhood updates</h3>\n      <p class="field-hint profile-settings-hint" data-i18n="settings.nbh.sub">When neighbours in your society report or resolve hazards.</p>\n      <div class="profile-settings">\n' + NBH_HTML + '      </div>\n\n' + IDX_ANCHOR,
        1,
    )
    IDX.write_text(idx, encoding="utf-8")
    print("index.html updated")

# sw.js
SW = ROOT / "sw.js"
sw = SW.read_text(encoding="utf-8")
sw = sw.replace("const CACHE = 'civicradar-v96';", "const CACHE = 'civicradar-v97';", 1)
if "notificationclick" not in sw:
    sw += """

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const data = (event.notification && event.notification.data) || {};
  const reportId = data.reportId || '';
  const target = data.url || './';
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if ('focus' in client) {
          client.postMessage({ type: 'nbh-alert-focus', reportId });
          return client.focus();
        }
      }
      const url = reportId ? `${target}${target.includes('?') ? '&' : '?'}report=${encodeURIComponent(reportId)}` : target;
      return self.clients.openWindow(url);
    })
  );
});
"""
    SW.write_text(sw, encoding="utf-8")
    print("sw.js updated")

# schema.sql
SCHEMA = ROOT / "supabase" / "schema.sql"
schema = SCHEMA.read_text(encoding="utf-8")
if "neighbourhood_new_alerts_enabled" not in schema:
    schema += """

-- =====================================================================
-- Neighbourhood alert preferences (v97)
-- =====================================================================
alter table public.profiles add column if not exists neighbourhood_new_alerts_enabled boolean;
alter table public.profiles add column if not exists neighbourhood_resolved_alerts_enabled boolean;

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own"
  on public.profiles for update
  to authenticated
  using (auth.uid() = id)
  with check (auth.uid() = id);
"""
    SCHEMA.write_text(schema, encoding="utf-8")
    print("schema.sql updated")

print("done")
