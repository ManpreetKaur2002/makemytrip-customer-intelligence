import { useEffect, useRef, useState } from "react";
import {
    Activity,
    ArrowDownRight,
    ArrowRight,
    ArrowUpRight,
    BadgeIndianRupee,
    Bell,
    BookOpenCheck,
    CalendarDays,
    Check,
    ChevronDown,
    CircleHelp,
    Clock3,
    Compass,
    CreditCard,
    Headphones,
    LayoutDashboard,
    LifeBuoy,
    LoaderCircle,
    MapPin,
    Menu,
    MessageSquareText,
    MoreHorizontal,
    Plane,
    Plus,
    Search,
    Send,
    Settings2,
    Sparkles,
    Users,
    X,
} from "lucide-react";
import { api, dashboardRequests } from "./api.js";

const navigation = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "customers", label: "Customers", icon: Users },
    { id: "bookings", label: "Bookings", icon: CalendarDays },
    { id: "support", label: "Support cases", icon: Headphones },
    { id: "preferences", label: "Preferences", icon: Settings2 },
    { id: "chat", label: "Travel assistant", icon: MessageSquareText },
];

const customerNavigation = [
    { id: "home", label: "Home", icon: Compass },
    { id: "trips", label: "My trips", icon: CalendarDays },
    { id: "preferences", label: "Preferences", icon: Settings2 },
    { id: "support", label: "Support", icon: Headphones },
    { id: "assistant", label: "Travel assistant", icon: MessageSquareText },
];

const emptyData = {
    summary: { customers: 0, bookings: 0, open_cases: 0 },
    customers: [],
    bookings: [],
    cases: [],
};

const dateLabel = (value, options = { month: "short", day: "numeric" }) => {
    if (!value) return "Not scheduled";
    return new Intl.DateTimeFormat("en-IN", options).format(new Date(value));
};

const moneyLabel = (amount, currency = "INR") => {
    if (amount === null || amount === undefined) return "—";
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency,
        maximumFractionDigits: 0,
    }).format(Number(amount));
};

function App() {
    return (
        <div className="customer-portal">
            <header className="customer-portal-header">
                <div className="customer-brand">
                    <div className="brand-mark"><Plane size={19} strokeWidth={2.8} /></div>
                    <div>
                        <div className="brand-name">makemytrip</div>
                        <div className="customer-brand-subtitle">TRAVEL ASSISTANT</div>
                    </div>
                </div>
                <div className="customer-portal-status"><span className="status-dot" />Customer account</div>
            </header>
            <main className="customer-portal-main">
                <CustomerChatView />
            </main>
        </div>
    );
}

function OperationsDashboard() {
    const [activeView, setActiveView] = useState("overview");
    const [data, setData] = useState(emptyData);
    const [loading, setLoading] = useState(true);
    const [refreshKey, setRefreshKey] = useState(0);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");
    const [modal, setModal] = useState("");
    const [query, setQuery] = useState("");
    const [mobileNavOpen, setMobileNavOpen] = useState(false);

    useEffect(() => {
        let active = true;
        setLoading(true);
        Promise.all(dashboardRequests.map(async ([key, path]) => [key, await api(path)]))
            .then((entries) => {
                if (!active) return;
                setData(Object.fromEntries(entries));
                setError("");
            })
            .catch((requestError) => {
                if (!active) return;
                setError(requestError.message || "Could not reach the API.");
            })
            .finally(() => {
                if (active) setLoading(false);
            });
        return () => {
            active = false;
        };
    }, [refreshKey]);

    const refresh = () => setRefreshKey((current) => current + 1);
    const announce = (message) => {
        setNotice(message);
        window.setTimeout(() => setNotice(""), 3200);
    };
    const changeView = (view) => {
        setActiveView(view);
        setMobileNavOpen(false);
        setQuery("");
    };
    const currentLabel = navigation.find((item) => item.id === activeView)?.label;

    return (
        <div className="app-shell">
            {mobileNavOpen && (
                <button
                    className="mobile-scrim"
                    aria-label="Close navigation"
                    onClick={() => setMobileNavOpen(false)}
                />
            )}
            <aside className={`sidebar ${mobileNavOpen ? "sidebar-open" : ""}`}>
                <div className="brand-lockup">
                    <div className="brand-mark"><Plane size={19} strokeWidth={2.8} /></div>
                    <div>
                        <div className="brand-name">makemytrip</div>
                        <div className="brand-product">TRIP OPERATIONS</div>
                    </div>
                    <button className="icon-button sidebar-close" aria-label="Close menu" onClick={() => setMobileNavOpen(false)}>
                        <X size={18} />
                    </button>
                </div>

                <div className="workspace-switcher">
                    <div className="workspace-avatar">IN</div>
                    <div className="workspace-copy">
                        <span>India operations</span>
                        <small>Customer experience</small>
                    </div>
                    <ChevronDown size={15} />
                </div>

                <div className="nav-caption">WORKSPACE</div>
                <nav className="primary-nav" aria-label="Main navigation">
                    {navigation.map(({ id, label, icon: Icon }) => (
                        <button
                            key={id}
                            className={`nav-item ${activeView === id ? "nav-item-active" : ""}`}
                            onClick={() => changeView(id)}
                        >
                            <Icon size={18} strokeWidth={1.9} />
                            <span>{label}</span>
                            {id === "support" && data.summary.open_cases > 0 && (
                                <span className="nav-count">{data.summary.open_cases}</span>
                            )}
                        </button>
                    ))}
                </nav>

                <div className="sidebar-bottom">
                    <div className="sidebar-rule" />
                    <button className="nav-item"><CircleHelp size={18} /><span>Help centre</span><ArrowUpRight size={14} /></button>
                    <div className="account-row">
                        <div className="account-avatar">AS</div>
                        <div className="account-copy"><span>Aarav Sharma</span><small>Operations lead</small></div>
                        <MoreHorizontal size={19} />
                    </div>
                </div>
            </aside>

            <main className="main-area">
                <header className="topbar">
                    <button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setMobileNavOpen(true)}>
                        <Menu size={20} />
                    </button>
                    <div className="breadcrumbs"><span>Workspace</span><span className="breadcrumb-slash">/</span><strong>{currentLabel}</strong></div>
                    <div className="topbar-actions">
                        <div className="api-indicator">
                            <span className={`status-dot ${error ? "status-dot-error" : ""}`} />
                            {error ? "API disconnected" : "API connected"}
                        </div>
                        <button className="icon-button notification-button" aria-label="Notifications" title="Notifications">
                            <Bell size={18} /><span />
                        </button>
                        <div className="topbar-divider" />
                        <div className="topbar-user"><div className="account-avatar account-avatar-small">AS</div><ChevronDown size={14} /></div>
                    </div>
                </header>

                <div className="page-wrap">
                    {error && (
                        <div className="error-banner" role="alert">
                            <span><strong>Can’t reach the backend.</strong> {error}</span>
                            <button onClick={refresh}>Retry</button>
                        </div>
                    )}
                    {activeView === "overview" && <Overview data={data} loading={loading} onNavigate={changeView} onCreateCustomer={() => setModal("customer")} />}
                    {activeView === "customers" && (
                        <CustomersView
                            customers={data.customers}
                            query={query}
                            onQuery={setQuery}
                            onCreate={() => setModal("customer")}
                            onNavigate={changeView}
                        />
                    )}
                    {activeView === "bookings" && (
                        <BookingsView
                            bookings={data.bookings}
                            customers={data.customers}
                            query={query}
                            onQuery={setQuery}
                            onCreate={() => setModal("booking")}
                        />
                    )}
                    {activeView === "support" && (
                        <SupportView
                            cases={data.cases}
                            customers={data.customers}
                            query={query}
                            onQuery={setQuery}
                            onCreate={() => setModal("support")}
                            onUpdated={refresh}
                            onNotice={announce}
                        />
                    )}
                    {activeView === "preferences" && (
                        <PreferencesView customers={data.customers} onNotice={announce} />
                    )}
                    {activeView === "chat" && <CustomerChatView />}
                </div>
            </main>

            {modal && (
                <RecordModal
                    kind={modal}
                    customers={data.customers}
                    bookings={data.bookings}
                    onClose={() => setModal("")}
                    onSaved={(message) => {
                        setModal("");
                        announce(message);
                        refresh();
                    }}
                />
            )}
            {notice && <div className="toast-message"><Check size={16} />{notice}</div>}
        </div>
    );
}

function PageHeading({ eyebrow, title, description, action }) {
    return (
        <div className="page-heading">
            <div>
                {eyebrow && <div className="eyebrow">{eyebrow}</div>}
                <h1>{title}</h1>
                {description && <p>{description}</p>}
            </div>
            {action}
        </div>
    );
}

function Overview({ data, loading, onNavigate, onCreateCustomer }) {
    const summary = data.summary;
    const latestBookings = data.bookings.slice(0, 4);
    const latestCases = data.cases.filter((item) => item.case_status !== "resolved" && item.case_status !== "closed").slice(0, 4);
    const bookingTypes = ["flight", "hotel", "holiday", "other"].map((type) => ({
        type,
        count: data.bookings.filter((booking) => booking.booking_type.toLowerCase() === type).length,
    }));
    const maxType = Math.max(...bookingTypes.map((item) => item.count), 1);

    return (
        <>
            <PageHeading
                eyebrow={dateLabel(new Date(), { weekday: "long", month: "long", day: "numeric" }).toUpperCase()}
                title="Operations overview"
                description="Your customer, booking and service activity at a glance."
                action={<button className="button button-primary" onClick={onCreateCustomer}><Plus size={16} />Add customer</button>}
            />
            <div className="welcome-strip">
                <div className="welcome-icon"><Compass size={21} /></div>
                <div className="welcome-copy"><strong>Good morning, Aarav</strong><span>Here’s what’s happening across your travel desk today.</span></div>
                <div className="welcome-date"><CalendarDays size={16} />{dateLabel(new Date(), { weekday: "short", month: "short", day: "numeric", year: "numeric" })}</div>
            </div>

            <div className="metrics-grid">
                <MetricCard label="Total customers" value={summary.customers} icon={Users} tone="coral" foot="Active customer profiles" loading={loading} />
                <MetricCard label="All bookings" value={summary.bookings} icon={CalendarDays} tone="amber" foot="Across flights, stays & trips" loading={loading} />
                <MetricCard label="Open support cases" value={summary.open_cases} icon={LifeBuoy} tone="mint" foot="Need a follow-up" loading={loading} />
                <MetricCard label="Pending bookings" value={data.bookings.filter((booking) => booking.booking_status === "pending").length} icon={Clock3} tone="blue" foot="Awaiting confirmation" loading={loading} />
            </div>

            <div className="overview-grid">
                <section className="surface-card booking-mix-card">
                    <PanelHeading title="Booking mix" subtitle="Reservations by travel type" action={<button className="text-action" onClick={() => onNavigate("bookings")}>All bookings <ArrowRight size={14} /></button>} />
                    <div className="booking-mix-total"><strong>{summary.bookings}</strong><span>total reservations</span><span className="mix-trend"><ArrowUpRight size={14} />Live</span></div>
                    <div className="mix-chart" aria-label="Bookings by travel type">
                        {bookingTypes.map((item) => (
                            <div className="mix-row" key={item.type}>
                                <span className="mix-label">{item.type}</span>
                                <div className="mix-track"><div className={`mix-fill mix-${item.type}`} style={{ width: `${Math.max((item.count / maxType) * 100, item.count ? 8 : 0)}%` }} /></div>
                                <strong>{item.count}</strong>
                            </div>
                        ))}
                    </div>
                    <div className="mix-legend"><span><i className="legend-dot legend-flight" />Flights</span><span><i className="legend-dot legend-hotel" />Hotels</span><span><i className="legend-dot legend-holiday" />Holidays</span></div>
                </section>

                <section className="surface-card quick-actions-card">
                    <PanelHeading title="Quick actions" subtitle="Common tasks, one click away" />
                    <div className="quick-action-list">
                        <button className="quick-action" onClick={() => onNavigate("customers")}><span className="quick-icon quick-coral"><Users size={17} /></span><span><strong>Find a customer</strong><small>Search the customer directory</small></span><ArrowRight size={16} /></button>
                        <button className="quick-action" onClick={() => onNavigate("bookings")}><span className="quick-icon quick-amber"><BookOpenCheck size={17} /></span><span><strong>Review bookings</strong><small>See upcoming and recent travel</small></span><ArrowRight size={16} /></button>
                        <button className="quick-action" onClick={() => onNavigate("support")}><span className="quick-icon quick-mint"><MessageSquareText size={17} /></span><span><strong>Resolve a case</strong><small>Keep support moving</small></span><ArrowRight size={16} /></button>
                    </div>
                </section>
            </div>

            <div className="overview-grid lower-grid">
                <section className="surface-card table-card">
                    <PanelHeading title="Recent bookings" subtitle="Latest reservations added" action={<button className="text-action" onClick={() => onNavigate("bookings")}>View all <ArrowRight size={14} /></button>} />
                    {latestBookings.length ? <BookingTable bookings={latestBookings} compact /> : <InlineEmpty icon={CalendarDays} title="No bookings yet" text="New reservations will show here." />}
                </section>
                <section className="surface-card table-card">
                    <PanelHeading title="Needs attention" subtitle="Open cases in your queue" action={<button className="text-action" onClick={() => onNavigate("support")}>Open queue <ArrowRight size={14} /></button>} />
                    {latestCases.length ? <CaseList cases={latestCases} customers={data.customers} compact /> : <InlineEmpty icon={Check} title="All clear" text="There are no open support cases." />}
                </section>
            </div>
        </>
    );
}

function MetricCard({ label, value, icon: Icon, tone, foot, loading }) {
    return (
        <article className="metric-card surface-card">
            <div className="metric-top"><span>{label}</span><div className={`metric-icon metric-${tone}`}><Icon size={18} /></div></div>
            <div className="metric-value">{loading ? <LoaderCircle className="spinner" size={27} /> : value.toLocaleString("en-IN")}</div>
            <div className="metric-foot"><span className="metric-trend"><Activity size={13} />Live data</span><span>{foot}</span></div>
        </article>
    );
}

function PanelHeading({ title, subtitle, action }) {
    return <div className="panel-heading"><div><h2>{title}</h2><p>{subtitle}</p></div>{action}</div>;
}

function CustomersView({ customers, query, onQuery, onCreate, onNavigate }) {
    const filtered = customers.filter((customer) => `${customer.full_name} ${customer.email || ""} ${customer.phone || ""}`.toLowerCase().includes(query.toLowerCase()));
    return (
        <>
            <PageHeading eyebrow="DIRECTORY" title="Customers" description="Customer profiles and travel relationships in one place." action={<button className="button button-primary" onClick={onCreate}><Plus size={16} />New customer</button>} />
            <section className="surface-card directory-card">
                <div className="list-toolbar"><div className="search-box"><Search size={16} /><input value={query} onChange={(event) => onQuery(event.target.value)} placeholder="Search name, email or phone" aria-label="Search customers" /></div><div className="toolbar-meta"><span className="count-label">{filtered.length} customers</span><button className="button button-quiet"><Settings2 size={15} />Filters</button></div></div>
                {filtered.length ? <div className="table-scroll"><table><thead><tr><th>Customer</th><th>Contact</th><th>Language</th><th>Status</th><th>Joined</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>
                    {filtered.map((customer) => <tr key={customer.customer_id}>
                        <td><div className="customer-cell"><Avatar name={customer.full_name} /><span><strong>{customer.full_name}</strong><small>Customer profile</small></span></div></td>
                        <td><span className="contact-main">{customer.email || "No email added"}</span><small className="table-subline">{customer.phone || "No phone added"}</small></td>
                        <td><span className="language-tag">{(customer.preferred_language || "en").toUpperCase()}</span></td>
                        <td><StatusPill value={customer.account_status} /></td>
                        <td>{dateLabel(customer.created_at)}</td>
                        <td><button className="table-icon-button" title="View bookings" aria-label={`View bookings for ${customer.full_name}`} onClick={() => onNavigate("bookings")}><ArrowRight size={16} /></button></td>
                    </tr>)}
                </tbody></table></div> : <EmptyState icon={Users} title={query ? "No matching customers" : "Your customer list is ready"} text={query ? "Try a different name, email or phone number." : "Add a customer profile to start organizing travel and support."} action={!query && <button className="button button-primary" onClick={onCreate}><Plus size={16} />Add customer</button>} />}
            </section>
        </>
    );
}

function BookingsView({ bookings, customers, query, onQuery, onCreate }) {
    const visible = bookings.filter((booking) => `${booking.booking_reference || ""} ${booking.destination || ""} ${booking.origin || ""} ${booking.booking_type}`.toLowerCase().includes(query.toLowerCase()));
    return (
        <>
            <PageHeading eyebrow="TRAVEL ACTIVITY" title="Bookings" description="Flights, stays and holidays booked by your customers." action={<button className="button button-primary" onClick={onCreate} disabled={!customers.length}><Plus size={16} />Add booking</button>} />
            <section className="surface-card directory-card">
                <div className="list-toolbar"><div className="search-box"><Search size={16} /><input value={query} onChange={(event) => onQuery(event.target.value)} placeholder="Search reference or destination" aria-label="Search bookings" /></div><div className="toolbar-meta"><span className="count-label">{visible.length} bookings</span><button className="button button-quiet"><CalendarDays size={15} />Any date<ChevronDown size={14} /></button></div></div>
                {visible.length ? <BookingTable bookings={visible} /> : <EmptyState icon={CalendarDays} title={query ? "No matching bookings" : "No bookings yet"} text={customers.length ? "Create a booking to track a customer's next trip." : "Add a customer first, then create their first booking."} action={customers.length > 0 && <button className="button button-primary" onClick={onCreate}><Plus size={16} />Create booking</button>} />}
            </section>
        </>
    );
}

function BookingTable({ bookings, compact = false }) {
    return (
        <div className="table-scroll"><table><thead><tr><th>Reference</th><th>Trip</th><th>Travel date</th><th>Amount</th><th>Status</th></tr></thead><tbody>
            {bookings.map((booking) => <tr key={booking.booking_id}>
                <td><span className="reference-code">{booking.booking_reference || booking.booking_id.slice(0, 8).toUpperCase()}</span><small className="table-subline">{booking.booking_type}</small></td>
                <td><div className="route-cell"><MapPin size={14} /><span>{booking.origin || "—"}</span><ArrowRight size={13} /><strong>{booking.destination || "Destination pending"}</strong></div></td>
                <td>{dateLabel(booking.departure_date)}{booking.return_date && <small className="table-subline">Return {dateLabel(booking.return_date)}</small>}</td>
                <td className="amount-cell">{moneyLabel(booking.amount, booking.currency)}</td>
                <td><StatusPill value={booking.booking_status} /></td>
            </tr>)}
        </tbody></table></div>
    );
}

function SupportView({ cases, customers, query, onQuery, onCreate, onUpdated, onNotice }) {
    const [statusFilter, setStatusFilter] = useState("open");
    const [updating, setUpdating] = useState("");
    const visible = cases.filter((item) => {
        const matchesStatus = statusFilter === "all"
            || (statusFilter === "high"
                ? item.priority === "high" && !["resolved", "closed"].includes(item.case_status)
                : statusFilter === "open"
                    ? !["resolved", "closed"].includes(item.case_status)
                    : item.case_status === statusFilter);
        const customer = customers.find((entry) => entry.customer_id === item.customer_id);
        return matchesStatus && `${item.issue_type} ${item.description || ""} ${customer?.full_name || ""}`.toLowerCase().includes(query.toLowerCase());
    });

    async function resolveCase(item) {
        setUpdating(item.case_id);
        try {
            await api(`/support-cases/${item.case_id}`, { method: "PATCH", body: JSON.stringify({ case_status: "resolved" }) });
            onNotice("Case marked as resolved");
            onUpdated();
        } catch (requestError) {
            onNotice(requestError.message);
        } finally {
            setUpdating("");
        }
    }

    return (
        <>
            <PageHeading eyebrow="CUSTOMER CARE" title="Support cases" description="Prioritize customer issues and keep every follow-up moving." action={<button className="button button-primary" onClick={onCreate} disabled={!customers.length}><Plus size={16} />New case</button>} />
            <div className="support-summary"><div><span className="support-summary-number">{cases.filter((item) => !["resolved", "closed"].includes(item.case_status)).length}</span><span>Open cases</span></div><div><span className="support-summary-number support-summary-urgent">{cases.filter((item) => item.priority === "high" && !["resolved", "closed"].includes(item.case_status)).length}</span><span>High priority</span></div><div><span className="support-summary-number">{cases.filter((item) => ["resolved", "closed"].includes(item.case_status)).length}</span><span>Resolved</span></div><div className="support-summary-note"><Clock3 size={15} />Keep your queue up to date</div></div>
            <section className="surface-card directory-card">
                <div className="list-toolbar support-toolbar"><div className="filter-tabs" role="tablist" aria-label="Filter support cases">{[["open", "Open"], ["high", "High priority"], ["all", "All cases"], ["resolved", "Resolved"]].map(([value, label]) => <button key={value} className={statusFilter === value ? "filter-tab filter-tab-active" : "filter-tab"} onClick={() => setStatusFilter(value)}>{label}</button>)}</div><div className="search-box support-search"><Search size={16} /><input value={query} onChange={(event) => onQuery(event.target.value)} placeholder="Search cases" aria-label="Search support cases" /></div></div>
                {visible.length ? <CaseList cases={visible} customers={customers} onResolve={resolveCase} updating={updating} /> : <EmptyState icon={LifeBuoy} title="No cases in this view" text={query ? "Try another search or filter." : "New customer issues will appear in this queue."} action={statusFilter !== "all" && <button className="button button-quiet" onClick={() => setStatusFilter("all")}>Show all cases</button>} />}
            </section>
        </>
    );
}

function CaseList({ cases, customers, onResolve, updating, compact = false }) {
    return <div className="case-list">{cases.map((item) => {
        const customer = customers.find((entry) => entry.customer_id === item.customer_id);
        return <article className="case-row" key={item.case_id}>
            <div className={`case-priority case-priority-${item.priority}`}><MessageSquareText size={17} /></div>
            <div className="case-main"><div className="case-heading"><strong>{item.issue_type.replaceAll("_", " ")}</strong><StatusPill value={item.case_status} /></div><p>{item.description || "No description provided."}</p><div className="case-meta"><span>{customer?.full_name || "Customer"}</span><span className="meta-separator">·</span><span>{dateLabel(item.created_at)}</span><span className="meta-separator">·</span><span className={`priority-label priority-${item.priority}`}>{item.priority} priority</span></div></div>
            {!compact && onResolve && !["resolved", "closed"].includes(item.case_status) && <button className="button button-quiet resolve-button" disabled={updating === item.case_id} onClick={() => onResolve(item)}>{updating === item.case_id ? <LoaderCircle className="spinner" size={15} /> : <Check size={15} />}Resolve</button>}
        </article>;
    })}</div>;
}

function PreferencesView({ customers, onNotice }) {
    const [customerId, setCustomerId] = useState(customers[0]?.customer_id || "");
    const [preference, setPreference] = useState(null);
    const [busy, setBusy] = useState(false);
    const [saving, setSaving] = useState(false);
    const [destinations, setDestinations] = useState("");
    const [dietary, setDietary] = useState("");

    useEffect(() => {
        if (!customerId) return;
        let active = true;
        setBusy(true);
        api(`/preferences/${customerId}`)
            .then((result) => {
                if (!active) return;
                setPreference(result);
                setDestinations((result.preferred_destinations || []).join(", "));
                setDietary((result.dietary_preferences || []).join(", "));
            })
            .catch((requestError) => {
                if (!active) return;
                if (requestError.status === 404) {
                    setPreference(null);
                    setDestinations("");
                    setDietary("");
                } else {
                    onNotice(requestError.message);
                }
            })
            .finally(() => active && setBusy(false));
        return () => { active = false; };
    }, [customerId, onNotice]);

    async function savePreferences(event) {
        event.preventDefault();
        setSaving(true);
        const form = new FormData(event.currentTarget);
        const readBudget = (value) => value === "" ? null : Number(value);
        const payload = {
            min_budget: readBudget(form.get("min_budget")),
            max_budget: readBudget(form.get("max_budget")),
            currency: form.get("currency"),
            preferred_destinations: destinations.split(",").map((value) => value.trim()).filter(Boolean),
            preferred_hotel_category: form.get("preferred_hotel_category") || null,
            travel_style: form.get("travel_style") || null,
            preferred_seat: form.get("preferred_seat") || null,
            dietary_preferences: dietary.split(",").map((value) => value.trim()).filter(Boolean),
        };
        try {
            const saved = await api(`/preferences/${customerId}`, { method: "PUT", body: JSON.stringify(payload) });
            setPreference(saved);
            onNotice("Travel preferences saved");
        } catch (requestError) {
            onNotice(requestError.message);
        } finally {
            setSaving(false);
        }
    }

    return (
        <>
            <PageHeading eyebrow="PERSONALIZATION" title="Travel preferences" description="Remember what each traveler values for their next trip." />
            {!customers.length ? <section className="surface-card"><EmptyState icon={Settings2} title="Add a customer first" text="Preferences are attached to a customer profile." /></section> : <div className="preferences-layout">
                <section className="surface-card preferences-customer"><div className="section-label">SELECT CUSTOMER</div><label className="select-with-icon"><Users size={16} /><select value={customerId} onChange={(event) => setCustomerId(event.target.value)}>{customers.map((customer) => <option value={customer.customer_id} key={customer.customer_id}>{customer.full_name}</option>)}</select><ChevronDown size={15} /></label><div className="preference-aside"><div className="preferences-aside-icon"><Settings2 size={18} /></div><strong>One traveler, a better trip</strong><p>Preferences help the team personalize destination suggestions, stays and in-flight support.</p></div><div className="preferences-aside-stats"><span>Profile</span><strong>{preference ? "Preferences saved" : "Not set up yet"}</strong></div></section>
                <form className="surface-card preference-form" onSubmit={savePreferences}>
                    <PanelHeading title="Trip essentials" subtitle="Set a comfortable budget and travel style." />
                    {busy ? <div className="loading-inline"><LoaderCircle className="spinner" size={19} />Loading preferences</div> : <>
                        <div className="form-grid form-grid-three"><Field label="Minimum budget" name="min_budget" type="number" min="0" step="0.01" defaultValue={preference?.min_budget ?? ""} placeholder="0.00" /><Field label="Maximum budget" name="max_budget" type="number" min="0" step="0.01" defaultValue={preference?.max_budget ?? ""} placeholder="0.00" /><SelectField label="Currency" name="currency" defaultValue={preference?.currency || "INR"} options={[["INR", "INR · Rupee"], ["USD", "USD · US Dollar"], ["AED", "AED · Dirham"], ["EUR", "EUR · Euro"]]} /></div>
                        <div className="form-grid form-grid-two"><Field label="Preferred destinations" value={destinations} onChange={(event) => setDestinations(event.target.value)} placeholder="Goa, Jaipur, Singapore" hint="Separate destinations with commas." /><SelectField label="Hotel category" name="preferred_hotel_category" defaultValue={preference?.preferred_hotel_category || ""} options={[["", "No preference"], ["3-star", "3 star"], ["4-star", "4 star"], ["5-star", "5 star"], ["boutique", "Boutique"]]} /></div>
                        <div className="form-grid form-grid-two"><SelectField label="Travel style" name="travel_style" defaultValue={preference?.travel_style || ""} options={[["", "Choose a style"], ["leisure", "Leisure"], ["adventure", "Adventure"], ["family", "Family"], ["business", "Business"], ["luxury", "Luxury"]]} /><SelectField label="Preferred seat" name="preferred_seat" defaultValue={preference?.preferred_seat || ""} options={[["", "No preference"], ["window", "Window"], ["aisle", "Aisle"], ["middle", "Middle"]]} /></div>
                        <Field label="Dietary preferences" value={dietary} onChange={(event) => setDietary(event.target.value)} placeholder="Vegetarian, Jain" hint="Separate preferences with commas." />
                        <div className="form-footer"><span>{preference ? "Changes save to this customer profile." : "This creates a preference profile for this customer."}</span><button className="button button-primary" disabled={saving}>{saving ? <LoaderCircle className="spinner" size={16} /> : <Check size={16} />}{saving ? "Saving" : "Save preferences"}</button></div>
                    </>}
                </form>
            </div>}
        </>
    );
}

function CustomerChatView() {
    const [customer, setCustomer] = useState(null);
    const [activePage, setActivePage] = useState("home");
    const [authLoading, setAuthLoading] = useState(true);
    const [authMode, setAuthMode] = useState("login");
    const [authBusy, setAuthBusy] = useState(false);
    const [authError, setAuthError] = useState("");
    const [sessions, setSessions] = useState([]);
    const [sessionId, setSessionId] = useState("");
    const [messages, setMessages] = useState([]);
    const [draft, setDraft] = useState("");
    const [loadingHistory, setLoadingHistory] = useState(false);
    const [sending, setSending] = useState(false);
    const [chatError, setChatError] = useState("");
    const [bookings, setBookings] = useState([]);
    const [supportCases, setSupportCases] = useState([]);
    const [accountDataError, setAccountDataError] = useState("");
    const messageListRef = useRef(null);

    useEffect(() => {
        const pageLabel = customerNavigation.find((item) => item.id === activePage)?.label;
        document.title = customer
            ? `${pageLabel} | MakeMyTrip`
            : authMode === "register"
                ? "Create account | MakeMyTrip"
                : "Sign in | MakeMyTrip";
    }, [activePage, authMode, customer]);

    useEffect(() => {
        let active = true;
        api("/auth/me")
            .then((profile) => active && setCustomer(profile))
            .catch((requestError) => {
                if (active && requestError.status !== 401) {
                    setAuthError(requestError.message);
                }
            })
            .finally(() => active && setAuthLoading(false));
        return () => { active = false; };
    }, []);

    useEffect(() => {
        if (!customer) {
            setBookings([]);
            setSupportCases([]);
            setAccountDataError("");
            return undefined;
        }
        let active = true;
        Promise.all([api("/me/bookings"), api("/me/support-cases")])
            .then(([customerBookings, customerCases]) => {
                if (!active) return;
                setBookings(customerBookings);
                setSupportCases(customerCases);
                setAccountDataError("");
            })
            .catch((requestError) => {
                if (active) setAccountDataError(requestError.message);
            });
        return () => { active = false; };
    }, [customer]);

    useEffect(() => {
        if (!customer) {
            setSessions([]);
            setSessionId("");
            setMessages([]);
            return undefined;
        }
        let active = true;
        setSessionId("");
        setMessages([]);
        api("/chat/sessions")
            .then((items) => {
                if (!active) return;
                setSessions(items);
                const storageKey = `trip-assistant-session:${customer.customer_id}`;
                const rememberedId = localStorage.getItem(storageKey);
                const remembered = items.find((item) => item.session_id === rememberedId);
                setSessionId(remembered?.session_id || items[0]?.session_id || "");
                setChatError("");
            })
            .catch((requestError) => active && setChatError(requestError.message));
        return () => { active = false; };
    }, [customer]);

    useEffect(() => {
        if (!customer || !sessionId) {
            setMessages([]);
            return undefined;
        }
        let active = true;
        setLoadingHistory(true);
        api(`/chat/sessions/${sessionId}/history`)
            .then((history) => {
                if (active) setMessages(history.messages.filter((item) => item.role !== "tool"));
            })
            .catch((requestError) => active && setChatError(requestError.message))
            .finally(() => active && setLoadingHistory(false));
        return () => { active = false; };
    }, [customer, sessionId]);

    useEffect(() => {
        messageListRef.current?.scrollTo({
            top: messageListRef.current.scrollHeight,
            behavior: "smooth",
        });
    }, [messages, sending]);

    async function submitAuth(event) {
        event.preventDefault();
        setAuthBusy(true);
        setAuthError("");
        const form = new FormData(event.currentTarget);
        const payload = {
            email: form.get("email"),
            password: form.get("password"),
        };
        if (authMode === "register") {
            payload.full_name = form.get("full_name");
        }
        try {
            const profile = await api(`/auth/${authMode === "register" ? "register" : "login"}`, {
                method: "POST",
                body: JSON.stringify(payload),
            });
            setCustomer(profile);
            setActivePage("home");
            setAuthError("");
        } catch (requestError) {
            setAuthError(requestError.message);
        } finally {
            setAuthBusy(false);
        }
    }

    async function logout() {
        await api("/auth/logout", { method: "POST" });
        if (customer) localStorage.removeItem(`trip-assistant-session:${customer.customer_id}`);
        setCustomer(null);
        setAuthMode("login");
        setActivePage("home");
        setChatError("");
    }

    async function startConversation() {
        setChatError("");
        try {
            const session = await api("/chat/sessions", {
                method: "POST",
                body: JSON.stringify({ title: "New conversation" }),
            });
            setSessions((current) => [session, ...current]);
            setSessionId(session.session_id);
            setMessages([]);
            localStorage.setItem(`trip-assistant-session:${customer.customer_id}`, session.session_id);
        } catch (requestError) {
            setChatError(requestError.message);
        }
    }

    function openConversation(session) {
        setSessionId(session.session_id);
        localStorage.setItem(`trip-assistant-session:${customer.customer_id}`, session.session_id);
        setChatError("");
    }

    async function sendMessage(text = draft) {
        const content = text.trim();
        if (!content || sending) return;
        setDraft("");
        setChatError("");
        setMessages((current) => [...current, { message_id: `local-${Date.now()}`, role: "user", content }]);
        setSending(true);
        try {
            const result = await api("/chat/messages", {
                method: "POST",
                body: JSON.stringify({ session_id: sessionId || null, message: content }),
            });
            if (!sessionId) {
                setSessionId(result.session_id);
                localStorage.setItem(`trip-assistant-session:${customer.customer_id}`, result.session_id);
                setSessions((current) => [
                    {
                        session_id: result.session_id,
                        title: content.slice(0, 42),
                        status: "active",
                        updated_at: new Date().toISOString(),
                    },
                    ...current.filter((item) => item.session_id !== result.session_id),
                ]);
            }
            setMessages((current) => [...current, { message_id: `reply-${Date.now()}`, role: "assistant", content: result.reply }]);
        } catch (requestError) {
            setChatError(requestError.message);
        } finally {
            setSending(false);
        }
    }

    const suggestions = ["Find my upcoming bookings", "Show my travel preferences", "I need help with a refund"];

    return (
        <>
            {customer && <nav className="customer-navigation" aria-label="Customer pages">
                <div className="customer-navigation-tabs">
                    {customerNavigation.map(({ id, label, icon: Icon }) => <button key={id} className={`customer-navigation-tab ${activePage === id ? "customer-navigation-tab-active" : ""}`} onClick={() => setActivePage(id)}><Icon size={16} /><span>{label}</span></button>)}
                </div>
                <div className="signed-in-customer"><span>{customer.full_name}</span><button className="button button-quiet" onClick={logout}>Sign out</button></div>
            </nav>}
            {(!customer || activePage === "assistant") && <PageHeading
                eyebrow={customer ? "CUSTOMER CONVERSATIONS" : "YOUR TRAVEL ACCOUNT"}
                title={customer ? "Travel assistant" : authMode === "register" ? "Create your account" : "Sign in"}
                description={customer
                    ? "A customer-facing concierge with persistent conversation history."
                    : authMode === "register"
                        ? "Create an account to get personalized help with your trips."
                        : "Sign in or create an account to get help with your trips."}
            />}
            {authLoading ? (
                <section className="surface-card auth-loading"><LoaderCircle className="spinner" size={19} />Checking your account</section>
            ) : !customer ? (
                <CustomerAuthPanel
                    mode={authMode}
                    setMode={(mode) => { setAuthMode(mode); setAuthError(""); }}
                    onSubmit={submitAuth}
                    busy={authBusy}
                    error={authError}
                />
            ) : activePage === "home" ? (
                <CustomerHomeView customer={customer} bookings={bookings} supportCases={supportCases} loading={Boolean(accountDataError)} onNavigate={setActivePage} />
            ) : activePage === "trips" ? (
                <CustomerTripsView bookings={bookings} onPlan={() => setActivePage("assistant")} error={accountDataError} />
            ) : activePage === "preferences" ? (
                <CustomerPreferencesView error={accountDataError} onSaved={() => setAccountDataError("")} />
            ) : activePage === "support" ? (
                <CustomerSupportView cases={supportCases} bookings={bookings} error={accountDataError} onCreated={(createdCase) => setSupportCases((current) => [createdCase, ...current])} />
            ) : (
                <div className="chat-workspace surface-card">
                    <aside className="chat-sessions">
                        <div className="chat-session-heading"><div><strong>Conversations</strong><small>Saved to your account</small></div><button className="icon-button" onClick={startConversation} aria-label="Start new conversation" title="New conversation"><Plus size={17} /></button></div>
                        <div className="chat-session-list">{sessions.length ? sessions.map((session) => <button key={session.session_id} className={`chat-session-item ${sessionId === session.session_id ? "chat-session-active" : ""}`} onClick={() => openConversation(session)}><span className="chat-session-mark"><MessageSquareText size={15} /></span><span><strong>{session.title || "Travel assistant"}</strong><small>{dateLabel(session.updated_at, { month: "short", day: "numeric" })}</small></span></button>) : <div className="chat-session-empty">Your conversations will be saved here.</div>}</div>
                        <button className="button button-quiet chat-new-button" onClick={startConversation}><Plus size={15} />New conversation</button>
                    </aside>
                    <section className="chat-panel">
                        <div className="chat-panel-header"><div className="assistant-avatar"><Sparkles size={17} /></div><div><strong>MakeMyTrip assistant</strong><small><span className="status-dot" />Signed in as {customer.full_name}</small></div><span className="chat-history-label"><Clock3 size={14} />History saved</span></div>
                        <div className="chat-message-list" ref={messageListRef} aria-live="polite">
                            {loadingHistory ? <div className="loading-inline"><LoaderCircle className="spinner" size={18} />Restoring conversation</div> : messages.length ? messages.map((message) => <ChatBubble key={message.message_id} message={message} />) : <div className="chat-welcome"><div className="chat-welcome-mark"><Plane size={20} /></div><h2>Where can we take you?</h2><p>Ask about a booking, your travel preferences or a support issue. Your conversation will be saved to your account.</p><div className="chat-suggestions">{suggestions.map((suggestion) => <button key={suggestion} onClick={() => sendMessage(suggestion)} disabled={sending}>{suggestion}<ArrowRight size={14} /></button>)}</div></div>}
                            {sending && <div className="chat-typing"><span /><span /><span /></div>}
                        </div>
                        {chatError && <div className="chat-error" role="alert">{chatError}</div>}
                        <form className="chat-composer" onSubmit={(event) => { event.preventDefault(); sendMessage(); }}>
                            <textarea value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); sendMessage(); } }} placeholder="Ask about a trip, booking or support issue..." aria-label="Message the travel assistant" rows="2" maxLength={4000} disabled={sending || loadingHistory} />
                            <div className="chat-composer-footer"><span><span>Enter</span> to send · <span>Shift + Enter</span> for a new line</span><button className="chat-send-button" type="submit" disabled={!draft.trim() || sending || loadingHistory} aria-label="Send message" title="Send message">{sending ? <LoaderCircle className="spinner" size={17} /> : <Send size={17} />}</button></div>
                        </form>
                        <div className="chat-disclaimer">Responses can be incorrect. Booking requests remain pending until confirmed by the travel provider.</div>
                    </section>
                </div>
            )}
        </>
    );
}

function CustomerHomeView({ customer, bookings, supportCases, loading, onNavigate }) {
    const firstName = customer.full_name.split(/\s+/)[0];
    const nextBooking = bookings.find((booking) => booking.booking_status !== "cancelled") || null;

    return (
        <>
            <PageHeading eyebrow="YOUR TRAVEL ACCOUNT" title={`Hello, ${firstName}`} description="Your trips and travel help, all in one place." />
            <section className="customer-home-hero">
                <div className="customer-home-hero-copy">
                    <span className="eyebrow">READY WHEN YOU ARE</span>
                    <h2>Where would you like to go next?</h2>
                    <p>Tell your travel assistant what you have in mind and explore your options together.</p>
                    <button className="button button-primary" onClick={() => onNavigate("assistant")}><MessageSquareText size={16} />Plan with the assistant</button>
                </div>
                <div className="customer-home-hero-mark"><Plane size={35} /></div>
            </section>
            <div className="customer-home-metrics">
                <article className="surface-card customer-home-metric"><span>My trips</span><strong>{loading ? "—" : bookings.length}</strong><button className="text-action" onClick={() => onNavigate("trips")}>View trips <ArrowRight size={14} /></button></article>
                <article className="surface-card customer-home-metric"><span>Support cases</span><strong>{loading ? "—" : supportCases.filter((item) => !["resolved", "closed"].includes(item.case_status)).length}</strong><button className="text-action" onClick={() => onNavigate("support")}>Get support <ArrowRight size={14} /></button></article>
            </div>
            <section className="surface-card customer-home-next">
                <PanelHeading title="Your travel" subtitle="Bookings and plans linked to your account" action={<button className="text-action" onClick={() => onNavigate("trips")}>All trips <ArrowRight size={14} /></button>} />
                {loading ? <div className="loading-inline"><LoaderCircle className="spinner" size={18} />Loading your trips</div> : nextBooking ? <BookingTable bookings={[nextBooking]} compact /> : <InlineEmpty icon={CalendarDays} title="No trips booked yet" text="When you have a booking, it will appear here." />}
            </section>
        </>
    );
}

function CustomerTripsView({ bookings, onPlan, error }) {
    return (
        <>
            <PageHeading eyebrow="YOUR TRAVEL" title="My trips" description="View bookings associated with your account." action={<button className="button button-primary" onClick={onPlan}><MessageSquareText size={16} />Plan a trip</button>} />
            {error && <div className="error-banner" role="alert">{error}</div>}
            <section className="surface-card directory-card">
                {bookings.length ? <BookingTable bookings={bookings} /> : <EmptyState icon={CalendarDays} title="No trips yet" text="Your bookings will appear here once they’re added to your account." action={<button className="button button-primary" onClick={onPlan}><MessageSquareText size={16} />Talk about a trip</button>} />}
            </section>
        </>
    );
}

function CustomerPreferencesView({ error: accountError, onSaved }) {
    const [preference, setPreference] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [destinations, setDestinations] = useState("");
    const [dietary, setDietary] = useState("");

    useEffect(() => {
        let active = true;
        api("/me/preferences")
            .then((result) => {
                if (!active) return;
                setPreference(result);
                setDestinations((result.preferred_destinations || []).join(", "));
                setDietary((result.dietary_preferences || []).join(", "));
            })
            .catch((requestError) => {
                if (!active) return;
                if (requestError.status === 404) {
                    setPreference(null);
                    setDestinations("");
                    setDietary("");
                } else {
                    setError(requestError.message);
                }
            })
            .finally(() => active && setLoading(false));
        return () => { active = false; };
    }, []);

    async function savePreferences(event) {
        event.preventDefault();
        setSaving(true);
        setError("");
        const form = new FormData(event.currentTarget);
        const budget = (value) => value === "" ? null : Number(value);
        const payload = {
            min_budget: budget(form.get("min_budget")),
            max_budget: budget(form.get("max_budget")),
            currency: form.get("currency"),
            preferred_destinations: destinations.split(",").map((item) => item.trim()).filter(Boolean),
            preferred_hotel_category: form.get("preferred_hotel_category") || null,
            travel_style: form.get("travel_style") || null,
            preferred_seat: form.get("preferred_seat") || null,
            dietary_preferences: dietary.split(",").map((item) => item.trim()).filter(Boolean),
        };
        try {
            const result = await api("/me/preferences", { method: "PUT", body: JSON.stringify(payload) });
            setPreference(result);
            onSaved();
        } catch (requestError) {
            setError(requestError.message);
        } finally {
            setSaving(false);
        }
    }

    return (
        <>
            <PageHeading eyebrow="PERSONALIZATION" title="Travel preferences" description="Save what matters to you so trip suggestions feel more relevant." />
            {(error || accountError) && <div className="error-banner" role="alert">{error || accountError}</div>}
            <form className="surface-card preference-form customer-preference-form" onSubmit={savePreferences}>
                <PanelHeading title="Trip essentials" subtitle="Your preferences are private to your account." />
                {loading ? <div className="loading-inline"><LoaderCircle className="spinner" size={18} />Loading preferences</div> : <>
                    <div className="form-grid form-grid-three"><Field label="Minimum budget" name="min_budget" type="number" min="0" step="0.01" defaultValue={preference?.min_budget ?? ""} placeholder="0.00" /><Field label="Maximum budget" name="max_budget" type="number" min="0" step="0.01" defaultValue={preference?.max_budget ?? ""} placeholder="0.00" /><SelectField label="Currency" name="currency" defaultValue={preference?.currency || "INR"} options={[["INR", "INR · Rupee"], ["USD", "USD · US Dollar"], ["AED", "AED · Dirham"], ["EUR", "EUR · Euro"]]} /></div>
                    <div className="form-grid form-grid-two"><Field label="Preferred destinations" value={destinations} onChange={(event) => setDestinations(event.target.value)} placeholder="Goa, Jaipur, Singapore" hint="Separate destinations with commas." /><SelectField label="Hotel category" name="preferred_hotel_category" defaultValue={preference?.preferred_hotel_category || ""} options={[["", "No preference"], ["3-star", "3 star"], ["4-star", "4 star"], ["5-star", "5 star"], ["boutique", "Boutique"]]} /></div>
                    <div className="form-grid form-grid-two"><SelectField label="Travel style" name="travel_style" defaultValue={preference?.travel_style || ""} options={[["", "Choose a style"], ["leisure", "Leisure"], ["adventure", "Adventure"], ["family", "Family"], ["business", "Business"], ["luxury", "Luxury"]]} /><SelectField label="Preferred seat" name="preferred_seat" defaultValue={preference?.preferred_seat || ""} options={[["", "No preference"], ["window", "Window"], ["aisle", "Aisle"], ["middle", "Middle"]]} /></div>
                    <Field label="Dietary preferences" value={dietary} onChange={(event) => setDietary(event.target.value)} placeholder="Vegetarian, Jain" hint="Separate preferences with commas." />
                    <div className="form-footer"><span>{preference ? "Saved to your account." : "Save preferences to personalize future suggestions."}</span><button className="button button-primary" disabled={saving}>{saving ? <LoaderCircle className="spinner" size={16} /> : <Check size={16} />}{saving ? "Saving" : "Save preferences"}</button></div>
                </>}
            </form>
        </>
    );
}

function CustomerSupportView({ cases, bookings, error, onCreated }) {
    const [saving, setSaving] = useState(false);
    const [formError, setFormError] = useState("");

    async function createCase(event) {
        event.preventDefault();
        setSaving(true);
        setFormError("");
        const form = new FormData(event.currentTarget);
        const bookingId = form.get("booking_id");
        try {
            const supportCase = await api("/me/support-cases", {
                method: "POST",
                body: JSON.stringify({
                    booking_id: bookingId || null,
                    issue_type: form.get("issue_type"),
                    description: form.get("description"),
                    priority: form.get("priority"),
                }),
            });
            onCreated(supportCase);
            event.currentTarget.reset();
        } catch (requestError) {
            setFormError(requestError.message);
        } finally {
            setSaving(false);
        }
    }

    return (
        <>
            <PageHeading eyebrow="CUSTOMER CARE" title="Support" description="Open a case and review support requests linked to your account." />
            {(error || formError) && <div className="error-banner" role="alert">{formError || error}</div>}
            <div className="customer-support-layout">
                <section className="surface-card customer-support-form">
                    <PanelHeading title="How can we help?" subtitle="A support case will be added to your account." />
                    <form onSubmit={createCase}>
                        <SelectField label="Issue type" name="issue_type" required options={[["booking_change", "Booking change"], ["cancellation", "Cancellation"], ["refund", "Refund"], ["payment", "Payment"], ["baggage", "Baggage"], ["other", "Other"]]} />
                        <SelectField label="Related booking (optional)" name="booking_id" defaultValue="" options={[["", "No booking selected"], ...bookings.map((item) => [item.booking_id, `${item.booking_reference || item.booking_id.slice(0, 8)} · ${item.destination || item.booking_type}`])]} />
                        <SelectField label="Priority" name="priority" defaultValue="medium" options={[["low", "Low"], ["medium", "Medium"], ["high", "High"]]} />
                        <Field label="Describe the issue" name="description" type="textarea" required placeholder="Tell us what happened and how we can help." />
                        <button className="button button-primary" disabled={saving}>{saving ? <LoaderCircle className="spinner" size={16} /> : <Plus size={16} />}{saving ? "Sending" : "Create support case"}</button>
                    </form>
                </section>
                <section className="surface-card customer-support-list">
                    <PanelHeading title="Your cases" subtitle="Recent support activity" />
                    {cases.length ? <div className="customer-case-list">{cases.map((item) => <article className="customer-case-item" key={item.case_id}><div className="customer-case-heading"><strong>{item.issue_type.replaceAll("_", " ")}</strong><StatusPill value={item.case_status} /></div><p>{item.description || "No description provided."}</p><div className="case-meta"><span>{dateLabel(item.created_at)}</span><span className="meta-separator">·</span><span className={`priority-label priority-${item.priority}`}>{item.priority} priority</span></div>{item.resolution && <div className="customer-case-resolution"><strong>Resolution</strong><span>{item.resolution}</span></div>}</article>)}</div> : <InlineEmpty icon={LifeBuoy} title="No support cases" text="You can open a case using the form." />}
                </section>
            </div>
        </>
    );
}

function CustomerAuthPanel({ mode, setMode, onSubmit, busy, error }) {
    const registering = mode === "register";
    return (
        <section className="customer-auth-card surface-card">
            <div className="auth-brand-mark"><Plane size={19} /></div>
            <div className="eyebrow">YOUR TRAVEL ACCOUNT</div>
            <h2>{registering ? "Create your account" : "Welcome back"}</h2>
            <p>{registering ? "Sign up to get trip help tailored to you, with conversations saved to your account." : "Sign in to see your saved conversations and get help with your trips."}</p>
            <form onSubmit={onSubmit}>
                {registering && <Field label="Full name" name="full_name" required autoFocus placeholder="Your name" />}
                <Field label="Email" name="email" type="email" required autoFocus={!registering} placeholder="you@example.com" />
                <Field label="Password" name="password" type="password" required minLength={registering ? 12 : 1} autoComplete={registering ? "new-password" : "current-password"} placeholder={registering ? "At least 12 characters" : "Your password"} />
                {error && <div className="form-error" role="alert">{error}</div>}
                <button className="button button-primary auth-submit" disabled={busy}>{busy ? <LoaderCircle className="spinner" size={16} /> : null}{busy ? "Please wait" : registering ? "Create account" : "Sign in"}</button>
            </form>
            <div className="auth-switch">{registering ? "Already have an account?" : "New to the travel assistant?"}<button onClick={() => setMode(registering ? "login" : "register")}>{registering ? "Sign in" : "Create account"}</button></div>
        </section>
    );
}

function ChatBubble({ message }) {
    const isUser = message.role === "user";
    return <article className={`chat-message ${isUser ? "chat-message-user" : "chat-message-assistant"}`}><div className="chat-message-avatar">{isUser ? <Users size={14} /> : <Sparkles size={14} />}</div><div className="chat-message-content"><div className="chat-message-label">{isUser ? "You" : "Travel assistant"}</div><p>{message.content}</p></div></article>;
}

function RecordModal({ kind, customers, bookings, onClose, onSaved }) {
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const titles = { customer: "Add a customer", booking: "Create a booking", support: "Open a support case" };
    const descriptions = { customer: "Create a profile for a traveler.", booking: "Add a reservation to a customer timeline.", support: "Capture an issue and route it to the right team." };

    async function handleSubmit(event) {
        event.preventDefault();
        setSaving(true);
        setError("");
        const form = new FormData(event.currentTarget);
        const value = (name) => form.get(name) || null;
        let path;
        let body;
        if (kind === "customer") {
            path = "/customers";
            body = { full_name: value("full_name"), email: value("email"), phone: value("phone"), preferred_language: value("preferred_language"), account_status: "active" };
        } else if (kind === "booking") {
            path = "/bookings";
            body = { customer_id: value("customer_id"), booking_reference: value("booking_reference"), booking_type: value("booking_type"), origin: value("origin"), destination: value("destination"), departure_date: value("departure_date"), return_date: value("return_date"), amount: value("amount") ? Number(value("amount")) : null, currency: value("currency"), booking_status: "confirmed" };
        } else {
            path = "/support-cases";
            body = { customer_id: value("customer_id"), booking_id: value("booking_id"), issue_type: value("issue_type"), description: value("description"), priority: value("priority"), case_status: "open", interaction_history: [] };
        }
        try {
            await api(path, { method: "POST", body: JSON.stringify(body) });
            onSaved(kind === "customer" ? "Customer added" : kind === "booking" ? "Booking created" : "Support case opened");
        } catch (requestError) {
            setError(requestError.message);
            setSaving(false);
        }
    }

    return (
        <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
            <section className="modal-panel" role="dialog" aria-modal="true" aria-labelledby="modal-title">
                <div className="modal-header"><div><div className="eyebrow">WORKSPACE RECORD</div><h2 id="modal-title">{titles[kind]}</h2><p>{descriptions[kind]}</p></div><button className="icon-button" aria-label="Close dialog" onClick={onClose}><X size={19} /></button></div>
                <form onSubmit={handleSubmit}>
                    {kind === "customer" && <div className="modal-fields"><Field label="Full name" name="full_name" required placeholder="e.g. Ananya Mehta" autoFocus /><div className="form-grid form-grid-two"><Field label="Email" name="email" type="email" placeholder="name@example.com" /><Field label="Phone" name="phone" type="tel" placeholder="+91 98765 43210" /></div><SelectField label="Preferred language" name="preferred_language" defaultValue="en" options={[["en", "English"], ["hi", "Hindi"], ["bn", "Bengali"], ["ta", "Tamil"], ["mr", "Marathi"]]} /></div>}
                    {kind === "booking" && <div className="modal-fields"><SelectField label="Customer" name="customer_id" required options={customers.map((customer) => [customer.customer_id, customer.full_name])} /><div className="form-grid form-grid-two"><SelectField label="Booking type" name="booking_type" required options={[["flight", "Flight"], ["hotel", "Hotel"], ["holiday", "Holiday package"], ["train", "Train"], ["bus", "Bus"]]} /><Field label="Booking reference" name="booking_reference" placeholder="MMT-240815" /></div><div className="form-grid form-grid-two"><Field label="Origin" name="origin" placeholder="Delhi" /><Field label="Destination" name="destination" placeholder="Goa" /></div><div className="form-grid form-grid-two"><Field label="Departure date" name="departure_date" type="date" /><Field label="Return date" name="return_date" type="date" /></div><div className="form-grid form-grid-two"><Field label="Amount" name="amount" type="number" min="0" step="0.01" placeholder="0.00" /><SelectField label="Currency" name="currency" defaultValue="INR" options={[["INR", "INR"], ["USD", "USD"], ["AED", "AED"], ["EUR", "EUR"]]} /></div></div>}
                    {kind === "support" && <div className="modal-fields"><SelectField label="Customer" name="customer_id" required options={customers.map((customer) => [customer.customer_id, customer.full_name])} /><SelectField label="Related booking (optional)" name="booking_id" defaultValue="" options={[["", "No booking selected"], ...bookings.map((booking) => [booking.booking_id, `${booking.booking_reference || booking.booking_id.slice(0, 8)} · ${booking.destination || booking.booking_type}`])]} /><div className="form-grid form-grid-two"><SelectField label="Issue type" name="issue_type" required options={[["booking_change", "Booking change"], ["cancellation", "Cancellation"], ["refund", "Refund"], ["payment", "Payment"], ["baggage", "Baggage"], ["other", "Other"]]} /><SelectField label="Priority" name="priority" defaultValue="medium" options={[["low", "Low"], ["medium", "Medium"], ["high", "High"]]} /></div><Field label="What happened?" name="description" as="textarea" required placeholder="Add details to help the team resolve this case." /></div>}
                    {error && <div className="form-error" role="alert">{error}</div>}
                    <div className="modal-footer"><button type="button" className="button button-quiet" onClick={onClose}>Cancel</button><button className="button button-primary" disabled={saving}>{saving ? <LoaderCircle className="spinner" size={16} /> : <Plus size={16} />}{saving ? "Saving" : kind === "customer" ? "Create customer" : kind === "booking" ? "Create booking" : "Open case"}</button></div>
                </form>
            </section>
        </div>
    );
}

function Field({ label, name, type = "text", value, onChange, defaultValue, placeholder, hint, required, min, step, minLength, maxLength, autoComplete, autoFocus }) {
    const inputProps = { id: name, name, type, value, defaultValue, onChange, placeholder, required, min, step, minLength, maxLength, autoComplete, autoFocus };
    return <label className="field" htmlFor={name}><span className="field-label">{label}{required && <i> *</i>}</span>{type === "textarea" ? <textarea {...inputProps} rows="3" /> : <input {...inputProps} />}{hint && <small className="field-hint">{hint}</small>}</label>;
}

function SelectField({ label, name, options, defaultValue, required, onChange }) {
    return <label className="field" htmlFor={name}><span className="field-label">{label}{required && <i> *</i>}</span><span className="select-wrap"><select id={name} name={name} defaultValue={defaultValue} required={required} onChange={onChange}>{options.map(([value, text]) => <option key={value} value={value}>{text}</option>)}</select><ChevronDown size={15} /></span></label>;
}

function Avatar({ name = "Traveler" }) {
    const initials = name.trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
    return <span className="customer-avatar">{initials || "T"}</span>;
}

function StatusPill({ value }) {
    const normalized = (value || "unknown").toLowerCase();
    return <span className={`status-pill pill-${normalized.replaceAll("_", "-")}`}><i />{normalized.replaceAll("_", " ")}</span>;
}

function InlineEmpty({ icon: Icon, title, text }) {
    return <div className="inline-empty"><div><Icon size={17} /></div><span><strong>{title}</strong><small>{text}</small></span></div>;
}

function EmptyState({ icon: Icon, title, text, action }) {
    return <div className="empty-state"><div className="empty-state-icon"><Icon size={22} /></div><h3>{title}</h3><p>{text}</p>{action}</div>;
}

export default App;