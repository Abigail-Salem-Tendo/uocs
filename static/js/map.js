/*
 * static/js/map.js
 *
 * Shared map renderer. Called from both the citizen outage map page and
 * the provider dashboard, pointed at the same /api/outages/map-data
 * endpoint. Keeps things basic: no clustering, just colored markers.
 *
 * Usage (after the Google Maps script tag loads with callback=initMap,
 * OR call renderOutageMap() yourself once the API is ready):
 *
 *   <div id="outage-map" style="height: 480px;"></div>
 *   <script>
 *     function initMap() {
 *       renderOutageMap("outage-map", "/api/outages/map-data");
 *     }
 *   </script>
 *   <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_KEY&callback=initMap" async></script>
 */

const STATUS_COLORS = {
  pending: "#e0a800",     // amber
"in progress": "#2b8cbe",
resolved: "#2e7d32",
};

const HOTSPOT_COLOR = "#c62828"; // red, overrides status color

function markerColorFor(report) {
if (report.isHotspot) return HOTSPOT_COLOR;
return STATUS_COLORS[report.status] || "#757575";
}

async function renderOutageMap(elementId, dataUrl, options = {}) {
  const center = options.center || { lat: 0.3476, lng: 32.5825 }; // Kampala
const zoom = options.zoom || 12;

const map = new google.maps.Map(document.getElementById(elementId), {
    center,
    zoom,
});

let reports;
try {
    const res = await fetch(dataUrl);
    if (!res.ok) throw new Error(`Map data request failed: ${res.status}`);
    reports = await res.json();
} catch (err) {
    console.error("Could not load outage map data:", err);
    return;
}

const infoWindow = new google.maps.InfoWindow();

reports.forEach((report) => {
    const marker = new google.maps.Marker({
    position: { lat: report.lat, lng: report.lng },
    map,
    title: report.type,
    icon: {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: markerColorFor(report),
        fillOpacity: 0.9,
        strokeWeight: report.isHotspot ? 2 : 1,
        strokeColor: "#ffffff",
        scale: report.isHotspot ? 9 : 7,
    },
    });

    marker.addListener("click", () => {
    infoWindow.setContent(`
        <strong>${report.type}</strong><br>
        Status: ${report.status}${report.isHotspot ? " (hotspot)" : ""}<br>
        ${report.description ? report.description : ""}
    `);
    infoWindow.open(map, marker);
    });
});
}