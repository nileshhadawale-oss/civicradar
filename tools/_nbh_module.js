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
