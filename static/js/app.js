/**
 * Disaster Evacuation PathFinding System - Alpine.js Application
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
        // State
        activeTab: 'dashboard',
        activeCity: 'Map 1',
        wsConnected: false,
        currentTime: new Date().toLocaleString(),
        
        // Data
        cityData: null,
        cityNodes: [],
        cityEdges: [],
        activeEvents: [],
        rescueTeams: [],
        activeMissions: [],
        resources: [],
        safeZones: [],
        metrics: {
            totalNodes: 0,
            activeDisasters: 0,
            blockedRoads: 0,
            zonesAtRisk: 0,
            availableSafeZones: 0
        },
        zoneSummary: [],
        blockedEdges: [],
        
        // Forms
        newDisaster: {
            type: 'flood',
            epicenter: '',
            radius: 2,
            severity: 'high',
            preview: false
        },
        selectedStrandedNode: '',
        strandedForm: {
            people_stranded: 0,
            injury_level: 'none',
            survival_chance: 1.0,
            rescue_cost: 0,
            capacity: 0
        },
        roadBlock: { nodeA: '', nodeB: '', reason: 'manual' },
        roadUnblock: '',
        dispatchForm: {
            targetNode: '',
            teamId: '',
            algorithm: 'auto'
        },
        dispatchResourceForm: {
            resourceId: '',
            safeZoneId: '',
            quantity: 50
        },
        
        // Algorithm Lab
        animationForm: {
            start: '',
            goal: '',
            algorithm: 'BFS',
            speed: 500
        },
        isAnimating: false,
        animationSteps: [],
        currentAnimationStep: 0,
        animationPlaying: false,
        animationResult: '',
        
        raceForm: {
            start: '',
            goal: ''
        },
        isRacing: false,
        raceResults: null,
        
        waveForm: {
            epicenter: '',
            maxHops: 5
        },
        showEvacuationWaveModal: false,
        
        // Algorithm comparison
        algorithmComparison: [],
        
        // Rescue operation enhancements
        closestTeam: null,
        showTeamFinder: false,
        missionVisualization: null,
        activeMissionForViz: null,
        
        // Graph visualization
        network: null,
        graphData: null,
        showHeatmap: false,
        heatmapData: [],
        
        // Charts
        charts: {},
        
        disasterDescriptions: {
            flood: 'Blocks low-elevation roads and bridge nodes. Spreads along water paths.',
            earthquake: 'Randomly blocks roads within radius. May isolate bridge nodes.',
            fire: 'Blocks roads in spread pattern. Increases risk scores of nearby nodes.',
            landslide: 'Blocks mountain or elevated roads. Can isolate nodes completely.'
        },
        
        // Initialization
        async init() {
            this.updateTime();
            setInterval(() => this.updateTime(), 1000);
            
            await this.loadCityData();
            this.initGraph();
            
            // Poll for updates every 3 seconds
            setInterval(() => this.refreshData(), 3000);
        },
        
        updateTime() {
            this.currentTime = new Date().toLocaleString();
        },
        
        async refreshData() {
            if (this.activeTab === 'dashboard' || this.activeTab === 'disaster') {
                await this.loadCityData();
                if (this.showHeatmap) {
                    await this.loadHeatmap();
                }
            }
            if (this.activeTab === 'rescue') {
                await this.loadRescueData();
            }
            if (this.activeTab === 'resources') {
                await this.loadResources();
            }
        },
        
        // API Calls
        async api(endpoint, options = {}) {
            const response = await fetch(`/api${endpoint}`, {
                headers: { 'Content-Type': 'application/json' },
                ...options
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'API Error');
            }
            return response.json();
        },
        
        async loadCityData() {
            try {
                const data = await this.api(`/city/${this.activeCity}`);
                this.cityData = data.city;
                this.activeEvents = data.events.filter(e => e.active);
                this.metrics = {
                    totalNodes: data.city.nodes.length,
                    activeDisasters: data.active_disasters,
                    blockedRoads: data.blocked_edges.length,
                    zonesAtRisk: 0,
                    availableSafeZones: data.safe_zones.filter(z => (z.current_occupancy || 0) < z.capacity).length
                };
                this.blockedEdges = data.blocked_edges;
                this.cityNodes = data.city.nodes.map(n => ({
                    id: n.id,
                    name: n.name || n.id,
                    type: n.type || 'intersection',
                    x: n.x,
                    y: n.y,
                    zone: n.zone,
                    people_stranded: n.people_stranded || 0,
                    injury_level: n.injury_level || 'none',
                    helipad: n.helipad || false,
                    risk_score: n.risk_score || 0
                }));
                
                // Set default values for forms
                if (this.cityNodes.length > 0 && !this.newDisaster.epicenter) {
                    this.newDisaster.epicenter = this.cityNodes[0].id;
                    this.animationForm.start = this.cityNodes[0].id;
                    this.animationForm.goal = this.cityNodes[this.cityNodes.length > 1 ? 1 : 0].id;
                    this.raceForm.start = this.cityNodes[0].id;
                    this.raceForm.goal = this.cityNodes[this.cityNodes.length > 1 ? 1 : 0].id;
                    this.waveForm.epicenter = this.cityNodes[0].id;
                }
                
                this.cityEdges = data.city.edges.map(e => ({
                    source: e.source,
                    target: e.target,
                    distance: e.distance_km,
                    time: e.base_travel_time_min,
                    blocked: data.blocked_edges.some(([u, v]) => 
                        (u === e.source && v === e.target) || (u === e.target && v === e.source)
                    ),
                    air_only: e.air_only,
                    road_type: e.road_type
                }));
                
                // Zone summary
                const zones = {};
                for (const node of this.cityNodes) {
                    if (!zones[node.zone]) {
                        zones[node.zone] = { zone: node.zone, risk: 'low', blocked: 0 };
                    }
                    if (node.risk_score > 0.8) zones[node.zone].risk = 'critical';
                    else if (node.risk_score > 0.5 && zones[node.zone].risk !== 'critical') zones[node.zone].risk = 'high';
                    else if (node.risk_score > 0.2 && zones[node.zone].risk === 'low') zones[node.zone].risk = 'medium';
                }
                for (const [u, v] of data.blocked_edges) {
                    const nodeU = this.cityNodes.find(n => n.id === u);
                    if (nodeU && zones[nodeU.zone]) zones[nodeU.zone].blocked++;
                }
                this.zoneSummary = Object.values(zones);
                
                // Update graph
                this.updateGraph();
                
            } catch (error) {
                console.error('Failed to load city data:', error);
            }
        },
        
        async loadRescueData() {
            try {
                const [teams, missions] = await Promise.all([
                    this.api(`/city/${this.activeCity}/rescue-teams`),
                    this.api(`/city/${this.activeCity}/missions`)
                ]);
                this.rescueTeams = teams.teams;
                this.activeMissions = missions.active;
            } catch (error) {
                console.error('Failed to load rescue data:', error);
            }
        },
        
        async loadResources() {
            try {
                const [resources, zones] = await Promise.all([
                    this.api('/resources'),
                    this.api(`/city/${this.activeCity}/safe-zones`)
                ]);
                this.resources = resources.inventory;
                this.resourceStats = resources.summary;
                this.activeShipments = resources.allocations.filter(a => a.status === 'in_transit');
                this.safeZones = zones.safe_zones;
            } catch (error) {
                console.error('Failed to load resources:', error);
            }
        },
        
        async loadHeatmap() {
            try {
                const data = await this.api(`/city/${this.activeCity}/heatmap`);
                this.heatmapData = data.heatmap;
                this.updateGraphHeatmap();
            } catch (error) {
                console.error('Failed to load heatmap:', error);
            }
        },
        
        // Graph Visualization
        initGraph() {
            if (!document.getElementById('graph-container')) return;
            
            // Wait for DOM
            setTimeout(() => this.updateGraph(), 100);
        },
        
        updateGraph() {
            const container = document.getElementById('graph-container');
            if (!container || !this.cityNodes.length) return;
            
            const nodes = new vis.DataSet(
                this.cityNodes.map(n => ({
                    id: n.id,
                    label: n.name,
                    x: n.x * 50,
                    y: n.y * 50,
                    color: this.getNodeColor(n),
                    shape: this.getNodeShape(n),
                    size: n.people_stranded > 0 ? 20 + Math.min(20, n.people_stranded / 5) : 15,
                    font: { color: '#cad3f5' }
                }))
            );
            
            const edges = new vis.DataSet(
                this.cityEdges.map(e => ({
                    from: e.source,
                    to: e.target,
                    color: e.blocked ? '#ed8796' : e.air_only ? '#91d7e3' : '#5b6078',
                    width: e.blocked ? 3 : 1,
                    dashes: e.air_only || e.blocked,
                    smooth: { type: 'continuous' }
                }))
            );
            
            const options = {
                physics: {
                    enabled: false
                },
                interaction: {
                    dragNodes: true,
                    dragView: true,
                    zoomView: true
                },
                nodes: {
                    borderWidth: 2,
                    borderWidthSelected: 3
                }
            };
            
            if (this.network) {
                this.network.destroy();
            }
            
            this.network = new vis.Network(container, { nodes, edges }, options);
        },
        
        getNodeColor(node) {
            if (this.showHeatmap && this.heatmapData.length > 0) {
                const heatData = this.heatmapData.find(h => h.node_id === node.id);
                if (heatData) {
                    const risk = heatData.risk_score;
                    if (risk > 0.8) return '#ed8796'; // critical - red
                    if (risk > 0.5) return '#f5a97f'; // high - orange
                    if (risk > 0.2) return '#eed49f'; // medium - yellow
                    return '#a6da95'; // low - green
                }
            }
            
            const colors = {
                safe_zone: '#a6da95',
                hospital: '#8aadf4',
                shelter: '#c6a0f6',
                bridge: '#f5a97f',
                intersection: '#5b6078'
            };
            return colors[node.type] || '#5b6078';
        },
        
        getNodeShape(node) {
            if (node.type === 'safe_zone') return 'dot';
            if (node.type === 'hospital') return 'square';
            if (node.type === 'bridge') return 'diamond';
            return 'dot';
        },
        
        updateGraphHeatmap() {
            if (!this.network || !this.heatmapData.length) return;
            
            const updates = this.heatmapData.map(h => ({
                id: h.node_id,
                color: this.getHeatmapColor(h.risk_score)
            }));
            
            this.network.body.data.nodes.update(updates);
        },
        
        getHeatmapColor(risk) {
            if (risk > 0.8) return { background: '#ed8796', border: '#c74e61' };
            if (risk > 0.5) return { background: '#f5a97f', border: '#d0825d' };
            if (risk > 0.2) return { background: '#eed49f', border: '#c9a855' };
            return { background: '#a6da95', border: '#7cb868' };
        },
        
        resetGraph() {
            this.showHeatmap = false;
            this.heatmapData = [];
            this.animationSteps = [];
            this.currentAnimationStep = 0;
            this.raceResults = null;
            this.updateGraph();
        },
        
        // Actions
        async changeCity() {
            await this.loadCityData();
            this.updateGraph();
            this.activeMissions = [];
            this.algorithmComparison = [];
        },
        
        async createDisaster() {
            try {
                const result = await this.api('/disasters/create', {
                    method: 'POST',
                    body: JSON.stringify({
                        city: this.activeCity,
                        disaster_type: this.newDisaster.type,
                        epicenter: this.newDisaster.epicenter,
                        radius: this.newDisaster.radius,
                        severity: this.newDisaster.severity
                    })
                });
                alert(result.message);
                await this.loadCityData();
            } catch (error) {
                alert('Failed to create disaster: ' + error.message);
            }
        },
        
        async resolveDisaster(eventId) {
            try {
                await this.api(`/disasters/${eventId}/resolve?city_id=${this.activeCity}`, { method: 'POST' });
                await this.loadCityData();
            } catch (error) {
                alert('Failed to resolve disaster: ' + error.message);
            }
        },
        
        async updateStranded() {
            try {
                await this.api(`/city/${this.activeCity}/stranded`, {
                    method: 'POST',
                    body: JSON.stringify({
                        city: this.activeCity,
                        node_id: this.selectedStrandedNode,
                        people_stranded: parseInt(this.strandedForm.people_stranded),
                        injury_level: this.strandedForm.injury_level,
                        survival_chance: parseFloat(this.strandedForm.survival_chance),
                        rescue_cost: parseInt(this.strandedForm.rescue_cost)
                    })
                });
                await this.loadCityData();
                alert('Node updated successfully');
            } catch (error) {
                alert('Failed to update: ' + error.message);
            }
        },
        
        async blockRoad() {
            try {
                await this.api(`/city/${this.activeCity}/block-road`, {
                    method: 'POST',
                    body: JSON.stringify({
                        city: this.activeCity,
                        node_a: this.roadBlock.nodeA,
                        node_b: this.roadBlock.nodeB,
                        reason: this.roadBlock.reason
                    })
                });
                await this.loadCityData();
                this.roadBlock = { nodeA: '', nodeB: '', reason: 'manual' };
            } catch (error) {
                alert('Failed to block road: ' + error.message);
            }
        },
        
        async unblockRoad() {
            if (!this.roadUnblock) return;
            try {
                const [nodeA, nodeB] = JSON.parse(this.roadUnblock);
                await this.api(`/city/${this.activeCity}/unblock-road`, {
                    method: 'POST',
                    body: JSON.stringify({
                        city: this.activeCity,
                        node_a: nodeA,
                        node_b: nodeB,
                        reason: 'manual'
                    })
                });
                await this.loadCityData();
                this.roadUnblock = '';
            } catch (error) {
                alert('Failed to unblock road: ' + error.message);
            }
        },
        
        // Rescue Operations
        async findClosestTeam() {
            if (!this.dispatchForm.targetNode) {
                alert('Please select a target node first');
                return;
            }
            
            try {
                const data = await this.api(`/city/${this.activeCity}/closest-team?target_node=${this.dispatchForm.targetNode}`);
                if (data.success) {
                    this.closestTeam = data;
                    this.dispatchForm.teamId = data.recommended_team.unit_id;
                    this.algorithmComparison = data.algorithm_comparison.map(r => ({
                        ...r,
                        recommended: r.Algorithm === data.recommended_algorithm.algorithm
                    }));
                    this.showTeamFinder = true;
                } else {
                    alert(data.message || 'No available teams found');
                }
            } catch (error) {
                alert('Failed to find closest team: ' + error.message);
            }
        },
        
        async dispatchTeam() {
            try {
                const result = await this.api('/missions/dispatch', {
                    method: 'POST',
                    body: JSON.stringify({
                        city: this.activeCity,
                        team_id: this.dispatchForm.teamId,
                        target_node: this.dispatchForm.targetNode,
                        algorithm: this.dispatchForm.algorithm
                    })
                });
                alert(`Mission ${result.mission.mission_id} created successfully!\nAlgorithm: ${result.algorithm_used}\nPath length: ${result.path.length} nodes`);
                this.showTeamFinder = false;
                this.closestTeam = null;
                await this.loadRescueData();
                this.dispatchForm = { targetNode: '', teamId: '', algorithm: 'auto' };
            } catch (error) {
                alert('Failed to dispatch: ' + error.message);
            }
        },
        
        async advanceMission(missionId) {
            try {
                // Get visualization data before advancing
                const vizData = await this.api(`/missions/${missionId}/step-visualization`);
                if (vizData.success && vizData.visualization) {
                    this.missionVisualization = vizData.visualization;
                    this.activeMissionForViz = missionId;
                    this.visualizeMissionStep(vizData.visualization);
                }
                
                // Advance the mission
                await this.api(`/missions/${missionId}/advance`, { method: 'POST' });
                await this.loadRescueData();
            } catch (error) {
                alert('Failed to advance: ' + error.message);
            }
        },
        
        visualizeMissionStep(viz) {
            if (!this.network) return;
            
            const updates = [];
            
            // Color all visited nodes so far
            for (const nodeId of viz.visited_nodes) {
                updates.push({
                    id: nodeId,
                    color: { background: '#8aadf4', border: '#5b8ad8' }
                });
            }
            
            // Highlight current node
            updates.push({
                id: viz.current_node,
                color: { background: '#a6da95', border: '#7cb868' },
                size: 25
            });
            
            // Highlight next node
            if (viz.next_node) {
                updates.push({
                    id: viz.next_node,
                    color: { background: '#eed49f', border: '#c9a855' },
                    size: 25
                });
            }
            
            // Highlight the path taken so far
            for (let i = 0; i < viz.path_so_far.length - 1; i++) {
                const from = viz.path_so_far[i];
                const to = viz.path_so_far[i + 1];
                // Note: Vis.js edges are harder to update individually, 
                // so we focus on node visualization
            }
            
            if (updates.length > 0) {
                this.network.body.data.nodes.update(updates);
            }
            
            // Show step info
            this.animationResult = `Step ${viz.step_number + 1} of ${viz.total_steps}: At ${viz.current_node}, moving to ${viz.next_node} using ${viz.algorithm}`;
        },
        
        async showMissionFullTraversal(missionId) {
            try {
                const vizData = await this.api(`/missions/${missionId}/step-visualization`);
                if (!vizData.success || !vizData.visualization) {
                    alert('No visualization data available');
                    return;
                }
                
                const viz = vizData.visualization;
                
                // Reset graph
                this.resetGraph();
                
                // Animate through all steps
                const allSteps = viz.visualization_steps;
                let stepIndex = 0;
                
                const animateStep = () => {
                    if (stepIndex >= allSteps.length) return;
                    
                    const step = allSteps[stepIndex];
                    this.renderAnimationStep(step);
                    
                    stepIndex++;
                    setTimeout(animateStep, 300);
                };
                
                animateStep();
                
            } catch (error) {
                alert('Failed to show traversal: ' + error.message);
            }
        },
        
        async confirmRescue(missionId, people) {
            try {
                await this.api(`/missions/${missionId}/confirm-rescue?people_rescued=${people}`, { method: 'POST' });
                await this.loadRescueData();
            } catch (error) {
                alert('Failed to confirm rescue: ' + error.message);
            }
        },
        
        async startReturn(missionId) {
            try {
                await this.api(`/missions/${missionId}/return`, { method: 'POST' });
                await this.loadRescueData();
            } catch (error) {
                alert('Failed to start return: ' + error.message);
            }
        },
        
        async clearCompletedMissions() {
            for (const mission of this.activeMissions.filter(m => m.status === 'rescued')) {
                try {
                    await this.api(`/missions/${mission.mission_id}/complete`, { method: 'POST' });
                } catch (e) {}
            }
            await this.loadRescueData();
        },
        
        getMissionBadgeClass(status) {
            const classes = {
                'en_route': 'badge-high',
                'arrived': 'badge-medium',
                'rescued': 'badge-low',
                'returning': 'badge-medium',
                'complete': 'badge-low'
            };
            return classes[status] || 'badge-medium';
        },
        
        // Resources
        async dispatchResource() {
            try {
                await this.api('/resources/dispatch', {
                    method: 'POST',
                    body: JSON.stringify({
                        resource_id: this.dispatchResourceForm.resourceId,
                        quantity: parseInt(this.dispatchResourceForm.quantity),
                        safe_zone_id: this.dispatchResourceForm.safeZoneId,
                        city: this.activeCity
                    })
                });
                await this.loadResources();
                alert('Shipment dispatched');
            } catch (error) {
                alert('Failed to dispatch: ' + error.message);
            }
        },
        
        async confirmDelivery(allocationId) {
            try {
                await this.api('/resources/confirm-delivery', {
                    method: 'POST',
                    body: JSON.stringify({ allocation_id: allocationId, city: this.activeCity })
                });
                await this.loadResources();
            } catch (error) {
                alert('Failed to confirm: ' + error.message);
            }
        },
        
        async runRecoveryCycle() {
            try {
                const result = await this.api('/resources/recovery-cycle', {
                    method: 'POST',
                    body: JSON.stringify({ city: this.activeCity })
                });
                alert(`Recovery cycle complete: ${result.result.recovered} civilians recovered`);
                await this.loadResources();
            } catch (error) {
                alert('Failed to run cycle: ' + error.message);
            }
        },
        
        // Heatmap
        async toggleHeatmap() {
            this.showHeatmap = !this.showHeatmap;
            if (this.showHeatmap) {
                await this.loadHeatmap();
            } else {
                this.updateGraph();
            }
        },
        
        // Animation
        async runAnimation() {
            if (!this.animationForm.start || !this.animationForm.goal) {
                alert('Please select start and goal nodes');
                return;
            }
            
            this.isAnimating = true;
            this.animationSteps = [];
            this.currentAnimationStep = 0;
            this.animationPlaying = false;
            this.animationResult = '';
            
            try {
                const data = await this.api(`/city/${this.activeCity}/algorithms/animate/${this.animationForm.algorithm}?start=${this.animationForm.start}&goal=${this.animationForm.goal}`);
                this.animationSteps = data.steps;
                this.animationResult = data.path ? 
                    `Path found! Length: ${data.path.length} nodes, Visited: ${data.visited_count} nodes` : 
                    'No path found';
                this.isAnimating = false;
                this.animationPlaying = true;
                this.playAnimation();
            } catch (error) {
                this.isAnimating = false;
                alert('Animation failed: ' + error.message);
            }
        },
        
        async playAnimation() {
            if (!this.animationPlaying || this.currentAnimationStep >= this.animationSteps.length) {
                this.animationPlaying = false;
                return;
            }
            
            this.renderAnimationStep(this.animationSteps[this.currentAnimationStep]);
            this.currentAnimationStep++;
            
            if (this.animationPlaying && this.currentAnimationStep < this.animationSteps.length) {
                setTimeout(() => this.playAnimation(), this.animationForm.speed);
            } else {
                this.animationPlaying = false;
            }
        },
        
        renderAnimationStep(step) {
            if (!this.network || !step) return;
            
            const updates = [];
            
            // Color visited nodes
            if (step.type === 'visit') {
                updates.push({
                    id: step.node,
                    color: { background: '#8aadf4', border: '#5b8ad8' }
                });
                
                // Color frontier nodes
                if (step.frontier) {
                    for (const nodeId of step.frontier) {
                        if (nodeId !== step.node) {
                            updates.push({
                                id: nodeId,
                                color: { background: '#eed49f', border: '#c9a855' }
                            });
                        }
                    }
                }
            }
            
            // Highlight final path
            if (step.type === 'goal_found' && step.path) {
                for (const nodeId of step.path) {
                    updates.push({
                        id: nodeId,
                        color: { background: '#a6da95', border: '#7cb868' }
                    });
                }
            }
            
            if (updates.length > 0) {
                this.network.body.data.nodes.update(updates);
            }
        },
        
        prevStep() {
            if (this.currentAnimationStep > 0) {
                this.currentAnimationStep--;
                this.resetGraph();
                for (let i = 0; i <= this.currentAnimationStep; i++) {
                    this.renderAnimationStep(this.animationSteps[i]);
                }
            }
        },
        
        nextStep() {
            if (this.currentAnimationStep < this.animationSteps.length - 1) {
                this.currentAnimationStep++;
                this.renderAnimationStep(this.animationSteps[this.currentAnimationStep]);
            }
        },
        
        playPauseAnimation() {
            this.animationPlaying = !this.animationPlaying;
            if (this.animationPlaying) {
                this.playAnimation();
            }
        },
        
        // Algorithm Race
        async runAlgorithmRace() {
            if (!this.raceForm.start || !this.raceForm.goal) {
                alert('Please select start and goal nodes');
                return;
            }
            
            this.isRacing = true;
            this.raceResults = null;
            
            try {
                const data = await this.api(`/city/${this.activeCity}/algorithms/race?start=${this.raceForm.start}&goal=${this.raceForm.goal}`);
                this.raceResults = data.results;
                this.isRacing = false;
                
                // Render race panels after DOM updates
                setTimeout(() => this.renderRacePanels(), 100);
            } catch (error) {
                this.isRacing = false;
                alert('Race failed: ' + error.message);
            }
        },
        
        renderRacePanels() {
            if (!this.raceResults) return;
            
            const algorithms = ['BFS', 'DFS', 'Dijkstra', 'A*', 'UCS'];
            
            for (const algo of algorithms) {
                const container = document.getElementById(`race-panel-${algo}`);
                if (!container) continue;
                
                const result = this.raceResults[algo];
                if (!result || result.error) continue;
                
                const nodes = new vis.DataSet(
                    this.cityNodes.map(n => ({
                        id: n.id,
                        label: n.name,
                        x: n.x * 30,
                        y: n.y * 30,
                        color: '#5b6078',
                        size: 10,
                        font: { size: 8, color: '#cad3f5' }
                    }))
                );
                
                const edges = new vis.DataSet(
                    this.cityEdges.map(e => ({
                        from: e.source,
                        to: e.target,
                        color: e.blocked ? '#ed8796' : '#3a3d4d',
                        width: 1,
                        dashes: e.blocked
                    }))
                );
                
                const network = new vis.Network(container, { nodes, edges }, {
                    physics: { enabled: false },
                    interaction: { dragNodes: false, dragView: true, zoomView: true }
                });
                
                // Animate the exploration
                let stepIndex = 0;
                const animate = () => {
                    if (stepIndex >= result.steps.length) {
                        // Show final path
                        if (result.path) {
                            const pathUpdates = result.path.map((nodeId, i) => ({
                                id: nodeId,
                                color: { background: '#a6da95', border: '#7cb868' }
                            }));
                            nodes.update(pathUpdates);
                        }
                        return;
                    }
                    
                    const step = result.steps[stepIndex];
                    if (step.type === 'visit') {
                        nodes.update({
                            id: step.node,
                            color: { background: '#8aadf4', border: '#5b8ad8' }
                        });
                    }
                    
                    stepIndex++;
                    setTimeout(animate, 100);
                };
                
                setTimeout(animate, 200);
            }
        },
        
        // Evacuation Wave
        async runEvacuationWave() {
            try {
                const data = await this.api(`/city/${this.activeCity}/evacuation-wave?epicenter=${this.waveForm.epicenter}&max_hops=${this.waveForm.maxHops}`);
                
                // Reset graph
                this.resetGraph();
                
                // Animate waves
                let waveIndex = 0;
                const animateWave = () => {
                    if (waveIndex >= data.waves.length) return;
                    
                    const wave = data.waves[waveIndex];
                    const color = `rgba(237, 135, 150, ${0.3 + (waveIndex / data.waves.length) * 0.5})`;
                    
                    const updates = wave.nodes.map(nodeId => ({
                        id: nodeId,
                        color: { background: color, border: '#ed8796' }
                    }));
                    
                    this.network.body.data.nodes.update(updates);
                    
                    waveIndex++;
                    setTimeout(animateWave, 800);
                };
                
                // Color epicenter
                this.network.body.data.nodes.update({
                    id: data.epicenter,
                    color: { background: '#ed8796', border: '#c74e61' }
                });
                
                setTimeout(animateWave, 500);
                this.showEvacuationWaveModal = false;
                
            } catch (error) {
                alert('Wave simulation failed: ' + error.message);
            }
        },
        
        // Reset
        async resetAll() {
            if (!confirm('Reset all runtime data? This will clear missions, disasters, and stranded people.')) return;
            
            try {
                // Resolve all disasters
                for (const event of this.activeEvents) {
                    await this.api(`/disasters/${event.event_id}/resolve?city_id=${this.activeCity}`, { method: 'POST' });
                }
                
                // Complete all missions
                for (const mission of this.activeMissions) {
                    try {
                        await this.api(`/missions/${mission.mission_id}/complete`, { method: 'POST' });
                    } catch (e) {}
                }
                
                await this.loadCityData();
                await this.loadRescueData();
                alert('System reset complete');
            } catch (error) {
                alert('Reset failed: ' + error.message);
            }
        },
        
        // Watchers
        init() {
            this.$watch('activeTab', (value) => {
                if (value === 'rescue') this.loadRescueData();
                if (value === 'resources') this.loadResources();
                if (value === 'algorithms') {
                    setTimeout(() => this.initGraph(), 100);
                }
            });
            
            this.$watch('dispatchForm.targetNode', async (value) => {
                if (value && this.dispatchForm.teamId) {
                    try {
                        const data = await this.api(`/city/${this.activeCity}/algorithms/compare?start=${this.dispatchForm.teamId}&goal=${value}`);
                        this.algorithmComparison = data.all_results.map(r => ({
                            ...r,
                            recommended: r.Algorithm === data.recommended.algorithm
                        }));
                        
                        // Update charts
                        setTimeout(() => this.updateComparisonCharts(), 100);
                    } catch (e) {
                        console.error('Failed to compare algorithms:', e);
                    }
                }
            });
            
            this.$watch('selectedStrandedNode', (value) => {
                if (value) {
                    const node = this.cityNodes.find(n => n.id === value);
                    if (node) {
                        this.strandedForm = {
                            people_stranded: node.people_stranded || 0,
                            injury_level: node.injury_level || 'none',
                            survival_chance: node.survival_chance || 1.0,
                            rescue_cost: node.rescue_cost || 0,
                            capacity: node.population_capacity || 500
                        };
                    }
                }
            });
        },
        
        updateComparisonCharts() {
            if (!this.algorithmComparison.length) return;
            
            const algorithms = this.algorithmComparison.map(r => r.Algorithm);
            const colors = algorithms.map(a => a === 'A*' ? '#a6da95' : '#8aadf4');
            
            // Nodes explored chart
            const ctx1 = document.getElementById('chart-nodes');
            if (ctx1) {
                if (this.charts.nodes) this.charts.nodes.destroy();
                this.charts.nodes = new Chart(ctx1, {
                    type: 'bar',
                    data: {
                        labels: algorithms,
                        datasets: [{
                            label: 'Nodes Explored',
                            data: this.algorithmComparison.map(r => r['Nodes Explored']),
                            backgroundColor: colors
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { ticks: { color: '#b8c0e0' }, grid: { color: '#494d64' } },
                            x: { ticks: { color: '#b8c0e0' }, grid: { color: '#494d64' } }
                        }
                    }
                });
            }
            
            // Time chart
            const ctx2 = document.getElementById('chart-time');
            if (ctx2) {
                if (this.charts.time) this.charts.time.destroy();
                this.charts.time = new Chart(ctx2, {
                    type: 'bar',
                    data: {
                        labels: algorithms,
                        datasets: [{
                            label: 'Time (ms)',
                            data: this.algorithmComparison.map(r => r['Time (ms)']),
                            backgroundColor: colors
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { ticks: { color: '#b8c0e0' }, grid: { color: '#494d64' } },
                            x: { ticks: { color: '#b8c0e0' }, grid: { color: '#494d64' } }
                        }
                    }
                });
            }
            
            // Path length chart
            const ctx3 = document.getElementById('chart-length');
            if (ctx3) {
                if (this.charts.length) this.charts.length.destroy();
                this.charts.length = new Chart(ctx3, {
                    type: 'bar',
                    data: {
                        labels: algorithms,
                        datasets: [{
                            label: 'Path Length',
                            data: this.algorithmComparison.map(r => r['Path Length']),
                            backgroundColor: colors
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { ticks: { color: '#b8c0e0' }, grid: { color: '#494d64' } },
                            x: { ticks: { color: '#b8c0e0' }, grid: { color: '#494d64' } }
                        }
                    }
                });
            }
        },
        
        // Computed helpers
        get affectedNodes() {
            const affectedIds = new Set(this.activeEvents.flatMap(e => e.affected_nodes || []));
            return this.cityNodes.filter(n => affectedIds.has(n.id));
        },
        
        get strandedNodes() {
            return this.cityNodes.filter(n => n.people_stranded > 0);
        },
        
        get availableTeams() {
            return this.rescueTeams.filter(t => t.status === 'available');
        }
    }));
});
