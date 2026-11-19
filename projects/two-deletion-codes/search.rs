// Standalone Rust bitset solver and calibrator for binary 2-deletion codes.
// Compile: rustc -O projects/two-deletion-codes/search.rs -o /tmp/two_del_search
// Zero external crates; deterministic PRNG from --seed and a shared cooperative search deadline.

use std::collections::BTreeSet;
use std::env;
use std::fs;
use std::time::{Duration, Instant};

const MAX_WORDS: usize = 64; // 64 * 64 = 4096 bits (covers up to n = 12)

#[derive(Clone)]
struct BitSet {
    w: [u64; MAX_WORDS],
    words_used: usize,
}

impl BitSet {
    fn new(n_verts: usize) -> Self {
        let words_used = (n_verts + 63) / 64;
        Self {
            w: [0u64; MAX_WORDS],
            words_used,
        }
    }

    #[inline(always)]
    fn set(&mut self, i: usize) {
        self.w[i >> 6] |= 1u64 << (i & 63);
    }

    #[inline(always)]
    fn clear(&mut self, i: usize) {
        self.w[i >> 6] &= !(1u64 << (i & 63));
    }

    #[inline(always)]
    fn test(&self, i: usize) -> bool {
        (self.w[i >> 6] >> (i & 63)) & 1 != 0
    }

    fn count(&self) -> usize {
        let mut s = 0usize;
        for k in 0..self.words_used {
            s += self.w[k].count_ones() as usize;
        }
        s
    }

    fn count_and(&self, other: &BitSet) -> usize {
        let mut s = 0usize;
        for k in 0..self.words_used {
            s += (self.w[k] & other.w[k]).count_ones() as usize;
        }
        s
    }

    fn is_empty(&self) -> bool {
        for k in 0..self.words_used {
            if self.w[k] != 0 {
                return false;
            }
        }
        true
    }

    fn clear_all(&mut self) {
        for k in 0..self.words_used {
            self.w[k] = 0;
        }
    }

    fn and_assign(&mut self, other: &BitSet) {
        for k in 0..self.words_used {
            self.w[k] &= other.w[k];
        }
    }

    fn and_not_assign(&mut self, other: &BitSet) {
        for k in 0..self.words_used {
            self.w[k] &= !other.w[k];
        }
    }

    fn for_each_bit<F: FnMut(usize)>(&self, mut f: F) {
        for k in 0..self.words_used {
            let mut x = self.w[k];
            let base = k << 6;
            while x != 0 {
                let tz = x.trailing_zeros() as usize;
                f(base + tz);
                x &= x - 1;
            }
        }
    }
}

struct Graph {
    n_verts: usize,
    adj: Vec<BitSet>,
    compat: Vec<BitSet>,
    deg: Vec<usize>,
}

impl Graph {
    fn build(n_bits: usize) -> Self {
        assert!(n_bits >= 3 && n_bits <= 12);
        let n_verts = 1usize << n_bits;
        let n_sub = 1usize << (n_bits - 2);
        let mut buckets: Vec<Vec<u16>> = vec![Vec::new(); n_sub];

        for x in 0..n_verts {
            let mut seen = Vec::with_capacity(66);
            for i in 0..n_bits {
                for j in (i + 1)..n_bits {
                    let mut sub = 0usize;
                    let mut pos = n_bits - 3;
                    for b in (0..n_bits).rev() {
                        let bit_idx = n_bits - 1 - b;
                        if bit_idx == i || bit_idx == j {
                            continue;
                        }
                        let bit = (x >> b) & 1;
                        sub |= bit << pos;
                        if pos > 0 {
                            pos -= 1;
                        }
                    }
                    seen.push(sub as u16);
                }
            }
            seen.sort_unstable();
            seen.dedup();
            for s in seen {
                buckets[s as usize].push(x as u16);
            }
        }

        let mut adj = vec![BitSet::new(n_verts); n_verts];
        for b in &buckets {
            for &u in b {
                let ui = u as usize;
                for &v in b {
                    let vi = v as usize;
                    if ui != vi {
                        adj[ui].set(vi);
                    }
                }
            }
        }

        let mut compat = vec![BitSet::new(n_verts); n_verts];
        let mut all_mask = BitSet::new(n_verts);
        for v in 0..n_verts {
            all_mask.set(v);
        }
        let mut deg = vec![0usize; n_verts];
        for u in 0..n_verts {
            deg[u] = adj[u].count();
            compat[u] = all_mask.clone();
            compat[u].and_not_assign(&adj[u]);
            compat[u].clear(u);
        }

        Graph {
            n_verts,
            adj,
            compat,
            deg,
        }
    }
}

#[derive(Clone)]
struct Rng(u64);

impl Rng {
    fn new(seed: u64) -> Self {
        Self(seed.wrapping_add(0x9E37_79B9_7F4A_7C15) | 1)
    }
    #[inline(always)]
    fn next_u64(&mut self) -> u64 {
        let mut x = self.0;
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        self.0 = x;
        x.wrapping_mul(0x2545_F491_4F6C_DD1D)
    }
    #[inline(always)]
    fn next_usize(&mut self, bound: usize) -> usize {
        (self.next_u64() % (bound as u64)) as usize
    }
}

fn fmt_word(v: usize, n_bits: usize) -> String {
    format!("{:0width$b}", v, width = n_bits)
}

fn verify_independent(g: &Graph, set: &[usize]) -> bool {
    for i in 0..set.len() {
        for j in (i + 1)..set.len() {
            if set[i] == set[j] || g.adj[set[i]].test(set[j]) {
                return false;
            }
        }
    }
    true
}

// Exact Bipartite MIS Recombination (König's theorem) on A union B
fn bipartite_crossover(g: &Graph, a: &[usize], b: &[usize], rng: &mut Rng) -> Vec<usize> {
    let mut in_a = BitSet::new(g.n_verts);
    let mut in_b = BitSet::new(g.n_verts);
    for &v in a {
        in_a.set(v);
    }
    for &v in b {
        in_b.set(v);
    }
    let mut common = Vec::new();
    let mut left = Vec::new();
    let mut right = Vec::new();
    for &v in a {
        if in_b.test(v) {
            common.push(v);
        } else {
            left.push(v);
        }
    }
    for &v in b {
        if !in_a.test(v) {
            right.push(v);
        }
    }
    // Shuffle left and right slightly so ties in matching can break differently
    for i in (1..left.len()).rev() {
        let j = rng.next_usize(i + 1);
        left.swap(i, j);
    }
    for i in (1..right.len()).rev() {
        let j = rng.next_usize(i + 1);
        right.swap(i, j);
    }

    let nl = left.len();
    let nr = right.len();
    let mut adj_lr: Vec<Vec<usize>> = vec![Vec::new(); nl];
    for i in 0..nl {
        let u = left[i];
        for j in 0..nr {
            if g.adj[u].test(right[j]) {
                adj_lr[i].push(j);
            }
        }
    }

    let mut match_l = vec![None; nl];
    let mut match_r = vec![None; nr];

    fn kuhn(
        u: usize,
        adj_lr: &[Vec<usize>],
        vis_r: &mut [bool],
        match_l: &mut [Option<usize>],
        match_r: &mut [Option<usize>],
    ) -> bool {
        for &r in &adj_lr[u] {
            if vis_r[r] {
                continue;
            }
            vis_r[r] = true;
            if match_r[r].is_none() || kuhn(match_r[r].unwrap(), adj_lr, vis_r, match_l, match_r) {
                match_r[r] = Some(u);
                match_l[u] = Some(r);
                return true;
            }
        }
        false
    }

    for u in 0..nl {
        let mut vis_r = vec![false; nr];
        kuhn(u, &adj_lr, &mut vis_r, &mut match_l, &mut match_r);
    }

    // König alternating BFS from unmatched L
    let mut z_l = vec![false; nl];
    let mut z_r = vec![false; nr];
    let mut queue = Vec::new();
    for u in 0..nl {
        if match_l[u].is_none() {
            z_l[u] = true;
            queue.push(u);
        }
    }
    let mut head = 0usize;
    while head < queue.len() {
        let u = queue[head];
        head += 1;
        for &r in &adj_lr[u] {
            if match_l[u] != Some(r) && !z_r[r] {
                z_r[r] = true;
                if let Some(u2) = match_r[r] {
                    if !z_l[u2] {
                        z_l[u2] = true;
                        queue.push(u2);
                    }
                }
            }
        }
    }

    let mut out = common;
    for i in 0..nl {
        if z_l[i] {
            out.push(left[i]);
        }
    }
    for j in 0..nr {
        if !z_r[j] {
            out.push(right[j]);
        }
    }
    debug_assert!(verify_independent(g, &out));
    out
}

struct ExactSolver<'a> {
    deadline: Instant,
    g: &'a Graph,
    best: Vec<usize>,
    nodes: u64,
    node_limit: u64,
    aborted: bool,
}

impl<'a> ExactSolver<'a> {
    fn solve(&mut self, cands: &BitSet, initial_best: Vec<usize>, node_limit: u64) -> Vec<usize> {
        self.best = initial_best;
        self.nodes = 0;
        self.node_limit = node_limit;
        self.aborted = false;
        let mut cur = Vec::new();
        let p = cands.clone();
        self.expand(p, &mut cur);
        self.best.clone()
    }

    fn color_order(&self, p: &BitSet) -> (Vec<usize>, Vec<usize>) {
        let mut uncolored = p.clone();
        let mut order = Vec::with_capacity(p.count());
        let mut bounds = Vec::with_capacity(p.count());
        let mut color = 0usize;

        while !uncolored.is_empty() {
            color += 1;
            let mut rem = uncolored.clone();
            while !rem.is_empty() {
                let mut chosen = usize::MAX;
                for k in 0..rem.words_used {
                    if rem.w[k] != 0 {
                        chosen = (k << 6) + rem.w[k].trailing_zeros() as usize;
                        break;
                    }
                }
                order.push(chosen);
                bounds.push(color);
                uncolored.clear(chosen);
                rem.and_assign(&self.g.adj[chosen]);
            }
        }
        (order, bounds)
    }

    fn expand(&mut self, mut p: BitSet, cur: &mut Vec<usize>) {
        if self.aborted {
            return;
        }
        if self.nodes >= self.node_limit || Instant::now() >= self.deadline {
            self.aborted = true;
            return;
        }
        self.nodes += 1;
        if p.is_empty() {
            if cur.len() > self.best.len() {
                self.best = cur.clone();
            }
            return;
        }
        let (order, bounds) = self.color_order(&p);
        for idx in (0..order.len()).rev() {
            if cur.len() + bounds[idx] <= self.best.len() {
                return;
            }
            let v = order[idx];
            p.clear(v);
            cur.push(v);
            let mut next_p = p.clone();
            next_p.and_assign(&self.g.compat[v]);
            self.expand(next_p, cur);
            cur.pop();
            if self.aborted {
                return;
            }
        }
    }
}

struct LocalState<'a> {
    deadline: Instant,
    g: &'a Graph,
    in_set: BitSet,
    set_vec: Vec<usize>,
    conf_count: Vec<u16>,
    conf_xor: Vec<u16>,
    free_mask: BitSet,
    free_list: Vec<usize>,
    one_tight: Vec<usize>,
    buckets: Vec<Vec<usize>>,
    active_owners: Vec<usize>,
    penalties: Vec<u32>,
}

impl<'a> LocalState<'a> {
    fn new(g: &'a Graph, deadline: Instant) -> Self {
        let n = g.n_verts;
        Self {
            deadline,
            g,
            in_set: BitSet::new(n),
            set_vec: Vec::with_capacity(64),
            conf_count: vec![0u16; n],
            conf_xor: vec![0u16; n],
            free_mask: BitSet::new(n),
            free_list: Vec::with_capacity(n),
            one_tight: Vec::with_capacity(256),
            buckets: vec![Vec::new(); n],
            active_owners: Vec::with_capacity(64),
            penalties: vec![1u32; n],
        }
    }

    fn reset(&mut self, seed_set: &[usize]) {
        self.in_set.clear_all();
        self.set_vec.clear();
        self.conf_count.fill(0);
        self.conf_xor.fill(0);
        for &v in seed_set {
            self.add_vertex_raw(v);
        }
    }

    #[inline(always)]
    fn add_vertex_raw(&mut self, v: usize) {
        debug_assert!(!self.in_set.test(v));
        self.in_set.set(v);
        self.set_vec.push(v);
        let vu = v as u16;
        self.g.adj[v].for_each_bit(|u| {
            self.conf_count[u] += 1;
            self.conf_xor[u] ^= vu;
        });
    }

    #[inline(always)]
    fn remove_vertex_raw(&mut self, v: usize) {
        debug_assert!(self.in_set.test(v));
        self.in_set.clear(v);
        if let Some(pos) = self.set_vec.iter().position(|&x| x == v) {
            self.set_vec.swap_remove(pos);
        }
        let vu = v as u16;
        self.g.adj[v].for_each_bit(|u| {
            self.conf_count[u] -= 1;
            self.conf_xor[u] ^= vu;
        });
    }

    // Residual minimum-degree greedy fill
    fn greedy_fill(&mut self, rng: &mut Rng, use_penalties: bool) {
        let n = self.g.n_verts;
        while Instant::now() < self.deadline {
            self.free_list.clear();
            self.free_mask.clear_all();
            for v in 0..n {
                if !self.in_set.test(v) && self.conf_count[v] == 0 {
                    self.free_list.push(v);
                    self.free_mask.set(v);
                }
            }
            if self.free_list.is_empty() {
                break;
            }
            let mut best_v = self.free_list[0];
            let mut best_score = u64::MAX;
            let mut ties = 0usize;
            for &v in &self.free_list {
                let rdeg = self.g.adj[v].count_and(&self.free_mask) as u64;
                let base = if use_penalties {
                    rdeg * 16 + (self.penalties[v] as u64)
                } else {
                    rdeg * 4096 + (self.g.deg[v] as u64)
                };
                if base < best_score {
                    best_score = base;
                    best_v = v;
                    ties = 1;
                } else if base == best_score {
                    ties += 1;
                    if rng.next_usize(ties) == 0 {
                        best_v = v;
                    }
                }
            }
            self.add_vertex_raw(best_v);
        }
    }

    fn scan_one_tight_and_try_12(&mut self, rng: &mut Rng) -> bool {
        let n = self.g.n_verts;
        if Instant::now() >= self.deadline {
            return false;
        }
        self.one_tight.clear();
        for &u in &self.active_owners {
            self.buckets[u].clear();
        }
        self.active_owners.clear();

        for v in 0..n {
            if !self.in_set.test(v) && self.conf_count[v] == 1 {
                self.one_tight.push(v);
                let u = self.conf_xor[v] as usize;
                if self.buckets[u].is_empty() {
                    self.active_owners.push(u);
                }
                self.buckets[u].push(v);
            }
        }
        for i in (1..self.active_owners.len()).rev() {
            let j = rng.next_usize(i + 1);
            self.active_owners.swap(i, j);
        }
        for idx in 0..self.active_owners.len() {
            let u = self.active_owners[idx];
            let len = self.buckets[u].len();
            if len < 2 {
                continue;
            }
            for i in 0..len {
                if Instant::now() >= self.deadline {
                    return false;
                }
                let v1 = self.buckets[u][i];
                for j in (i + 1)..len {
                    let v2 = self.buckets[u][j];
                    if !self.g.adj[v1].test(v2) {
                        self.remove_vertex_raw(u);
                        self.add_vertex_raw(v1);
                        self.add_vertex_raw(v2);
                        self.greedy_fill(rng, false);
                        return true;
                    }
                }
            }
        }
        false
    }

    fn try_two_three_improve(&mut self, rng: &mut Rng) -> bool {
        let n = self.g.n_verts;
        let s_len = self.set_vec.len();
        if s_len < 2 {
            return false;
        }
        let mut pairs: Vec<(usize, usize)> = Vec::new();
        for i in 0..s_len {
            for j in (i + 1)..s_len {
                let a = self.set_vec[i].min(self.set_vec[j]);
                let b = self.set_vec[i].max(self.set_vec[j]);
                pairs.push((a, b));
            }
        }
        for i in (1..pairs.len()).rev() {
            let j = rng.next_usize(i + 1);
            pairs.swap(i, j);
        }
        let mut solver = ExactSolver {
            deadline: self.deadline,
            g: self.g,
            best: Vec::new(),
            nodes: 0,
            node_limit: 20_000,
            aborted: false,
        };
        for (u1, u2) in pairs {
            if Instant::now() >= self.deadline {
                return false;
            }
            let mut cands = BitSet::new(n);
            let mut count = 0usize;
            for v in 0..n {
                if self.in_set.test(v) {
                    continue;
                }
                let c = self.conf_count[v];
                if c == 1 {
                    let x = self.conf_xor[v] as usize;
                    if x == u1 || x == u2 {
                        cands.set(v);
                        count += 1;
                    }
                } else if c == 2 {
                    if self.g.adj[v].test(u1) && self.g.adj[v].test(u2) {
                        cands.set(v);
                        count += 1;
                    }
                }
            }
            if count >= 3 {
                let res = solver.solve(&cands, vec![u1, u2], 20_000);
                if res.len() > 2 {
                    self.remove_vertex_raw(u1);
                    self.remove_vertex_raw(u2);
                    for v in res {
                        if !self.in_set.test(v) && self.conf_count[v] == 0 {
                            self.add_vertex_raw(v);
                        }
                    }
                    self.greedy_fill(rng, false);
                    return true;
                }
            }
        }
        false
    }

    fn force_push(&mut self, rng: &mut Rng) {
        let n = self.g.n_verts;
        let mut low_conf = Vec::new();
        for v in 0..n {
            if !self.in_set.test(v) && self.conf_count[v] >= 1 && self.conf_count[v] <= 3 {
                low_conf.push(v);
            }
        }
        if low_conf.is_empty() || Instant::now() >= self.deadline {
            return;
        }
        let v = low_conf[rng.next_usize(low_conf.len())];
        let blockers: Vec<usize> = self
            .set_vec
            .iter()
            .copied()
            .filter(|&u| self.g.adj[v].test(u))
            .collect();
        for u in blockers {
            self.remove_vertex_raw(u);
        }
        self.add_vertex_raw(v);
        self.greedy_fill(rng, false);
    }

    fn plateau_search(
        &mut self,
        rng: &mut Rng,
        max_steps: usize,
        tabu_until: &mut [usize],
        step_counter: &mut usize,
        best_local: &mut Vec<usize>,
    ) {
        self.greedy_fill(rng, false);
        while self.scan_one_tight_and_try_12(rng) {}
        if self.set_vec.len() > best_local.len() {
            *best_local = self.set_vec.clone();
        }

        let mut no_improve = 0usize;
        for _ in 0..max_steps {
            if Instant::now() >= self.deadline {
                break;
            }
            *step_counter += 1;
            if self.scan_one_tight_and_try_12(rng) {
                if self.set_vec.len() > best_local.len() {
                    *best_local = self.set_vec.clone();
                }
                no_improve = 0;
                continue;
            }
            if self.one_tight.is_empty() {
                break;
            }

            let mut chosen = None;
            let mut best_tie = 0usize;
            for &v in &self.one_tight {
                if tabu_until[v] <= *step_counter {
                    best_tie += 1;
                    if rng.next_usize(best_tie) == 0 {
                        chosen = Some(v);
                    }
                }
            }
            let v_add = match chosen {
                Some(v) => v,
                None => self.one_tight[rng.next_usize(self.one_tight.len())],
            };
            let u_rem = self.conf_xor[v_add] as usize;
            tabu_until[u_rem] = *step_counter + 7 + rng.next_usize(7);
            self.remove_vertex_raw(u_rem);
            self.add_vertex_raw(v_add);
            self.greedy_fill(rng, false);
            if self.set_vec.len() > best_local.len() {
                *best_local = self.set_vec.clone();
                no_improve = 0;
            } else {
                no_improve += 1;
                if no_improve >= 120 {
                    break;
                }
            }
        }
    }

    fn exact_lns_step(
        &mut self,
        rng: &mut Rng,
        k_drop: usize,
        node_limit: u64,
        best_local: &mut Vec<usize>,
    ) -> bool {
        let n = self.g.n_verts;
        if self.set_vec.len() <= k_drop || Instant::now() >= self.deadline {
            return false;
        }
        let mut droppable = self.set_vec.clone();
        for i in (1..droppable.len()).rev() {
            let j = rng.next_usize(i + 1);
            droppable.swap(i, j);
        }
        let dropped: Vec<usize> = droppable[..k_drop].to_vec();
        for &u in &dropped {
            self.remove_vertex_raw(u);
        }
        let mut cands = BitSet::new(n);
        let mut cand_count = 0usize;
        for v in 0..n {
            if !self.in_set.test(v) && self.conf_count[v] == 0 {
                cands.set(v);
                cand_count += 1;
            }
        }
        let improved = if cand_count <= 240 {
            let mut solver = ExactSolver {
                deadline: self.deadline,
                g: self.g,
                best: Vec::new(),
                nodes: 0,
                node_limit,
                aborted: false,
            };
            // Pass an empty initial best of size dropped.len() - 1 so equal-size distinct solutions are found!
            let mut dummy_init = if dropped.len() > 1 {
                dropped[..dropped.len() - 1].to_vec()
            } else {
                Vec::new()
            };
            let sol = solver.solve(&cands, dummy_init.clone(), node_limit);
            if sol.len() > dropped.len() {
                for &v in &sol {
                    self.add_vertex_raw(v);
                }
                true
            } else if sol.len() == dropped.len() {
                // Accept the distinct equal-size completion to diffuse across the plateau!
                for &v in &sol {
                    self.add_vertex_raw(v);
                }
                false
            } else {
                dummy_init.clear();
                for &u in &dropped {
                    self.add_vertex_raw(u);
                }
                false
            }
        } else {
            for &u in &dropped {
                self.add_vertex_raw(u);
            }
            false
        };
        if self.set_vec.len() > best_local.len() {
            *best_local = self.set_vec.clone();
        }
        improved
    }
}

fn calibrate_small(g_max_exact: usize, deadline: Instant, node_limit: u64) {
    println!(
        "=== Calibration: OEIS A057591 exact optima (n = 3..{}) ===",
        g_max_exact
    );
    let expected = [0, 1, 1, 2, 2, 2, 4, 5, 7, 11, 16];
    for n in 3..=g_max_exact {
        let t0 = Instant::now();
        if t0 >= deadline {
            break;
        }
        let g = Graph::build(n);
        let mut all = BitSet::new(g.n_verts);
        for v in 0..g.n_verts {
            all.set(v);
        }
        let mut solver = ExactSolver {
            deadline,
            g: &g,
            best: Vec::new(),
            nodes: 0,
            node_limit,
            aborted: false,
        };
        let best = solver.solve(&all, Vec::new(), node_limit);
        assert!(verify_independent(&g, &best));
        if solver.aborted {
            println!("  n={}: incomplete, incumbent = {} (nodes={})", n, best.len(), solver.nodes);
            break;
        }
        assert_eq!(best.len(), expected[n], "mismatch at n={}", n);
        println!(
            "  n={:2} (V={:4}): exact a({}) = {:2} (nodes={}, {:.3}s)",
            n,
            g.n_verts,
            n,
            best.len(),
            solver.nodes,
            t0.elapsed().as_secs_f64()
        );
    }
}

fn collect_n11_halves(g11: &Graph, seed: u64, deadline: Instant) -> Vec<Vec<usize>> {
    let mut rng = Rng::new(seed);
    let mut ls = LocalState::new(g11, deadline);
    let mut tabu = vec![0usize; g11.n_verts];
    let mut step = 0usize;
    let mut found_sets: BTreeSet<Vec<usize>> = BTreeSet::new();

    while Instant::now() < deadline {
        let mut best_local = Vec::new();
        ls.reset(&[]);
        for _ in 0..3 {
            let mut free = Vec::new();
            for v in 0..g11.n_verts {
                if !ls.in_set.test(v) && ls.conf_count[v] == 0 {
                    free.push(v);
                }
            }
            if free.is_empty() {
                break;
            }
            let pick = free[rng.next_usize(free.len())];
            ls.add_vertex_raw(pick);
        }
        ls.plateau_search(&mut rng, 300, &mut tabu, &mut step, &mut best_local);
        if ls.set_vec.len() < 24 {
            for k in [6, 8] {
                if ls.exact_lns_step(&mut rng, k, 50_000, &mut best_local)
                    && ls.set_vec.len() == 24
                {
                    break;
                }
            }
        }
        if ls.set_vec.len() == 24 {
            assert!(verify_independent(g11, &ls.set_vec));
            let mut sorted = ls.set_vec.clone();
            sorted.sort_unstable();
            found_sets.insert(sorted);
        }
    }
    found_sets.into_iter().collect()
}

fn solve_opposite_half(
    g12: &Graph, half0_n11: &[usize], deadline: Instant, node_limit: u64,
) -> (Vec<usize>, bool) {
    let mut fixed = Vec::with_capacity(half0_n11.len());
    for &v in half0_n11 {
        fixed.push(v << 1);
    }
    let mut cands = BitSet::new(g12.n_verts);
    for v in 0..g12.n_verts {
        if (v & 1) == 1 {
            let mut ok = true;
            for &f in &fixed {
                if g12.adj[v].test(f) {
                    ok = false;
                    break;
                }
            }
            if ok {
                cands.set(v);
            }
        }
    }
    let mut solver = ExactSolver {
        deadline,
        g: g12,
        best: Vec::new(),
        nodes: 0,
        node_limit,
        aborted: false,
    };
    let opp = solver.solve(&cands, Vec::new(), node_limit);
    let mut full = fixed;
    full.extend(opp);
    assert!(verify_independent(g12, &full));
    (full, !solver.aborted)
}

fn update_global_best(
    g: &Graph,
    cand: &[usize],
    regime_label: &str,
    global_best: &mut Vec<usize>,
    best_regime: &mut String,
) {
    if cand.len() > global_best.len() {
        assert!(verify_independent(g, cand));
        *global_best = cand.to_vec();
        *best_regime = regime_label.to_string();
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let mut budget_secs = 240.0f64;
    let mut seed = 20261119u64;
    let mut out_path = String::from("two-deletion-search-output.txt");
    let mut calibrate_only = false;
    let mut max_exact_n = 9usize;

    let mut idx = 1;
    while idx < args.len() {
        match args[idx].as_str() {
            "--budget-secs" => {
                idx += 1;
                budget_secs = args[idx].parse().expect("valid float for --budget-secs");
            }
            "--seed" => {
                idx += 1;
                seed = args[idx].parse().expect("valid u64 for --seed");
            }
            "--out" => {
                idx += 1;
                out_path = args[idx].clone();
            }
            "--calibrate-only" => {
                calibrate_only = true;
                max_exact_n = 10;
            }
            "--max-exact-n" => {
                idx += 1;
                max_exact_n = args[idx].parse().expect("valid usize for --max-exact-n");
            }
            _ => panic!("Unknown arg: {}", args[idx]),
        }
        idx += 1;
    }

    let duration = Duration::try_from_secs_f64(budget_secs).ok();
    let Some(deadline) = duration.and_then(|d| Instant::now().checked_add(d)) else {
        eprintln!("--budget-secs must be finite, nonnegative and representable");
        std::process::exit(2);
    };
    if max_exact_n > 10 {
        eprintln!("--max-exact-n must be at most 10");
        std::process::exit(2);
    }
    println!(
        "Two-deletion solver | seed={} | search_budget_secs={} | calibrate_only={}",
        seed, budget_secs, calibrate_only
    );

    calibrate_small(max_exact_n, deadline, 50_000_000);

    let t_n11 = Instant::now();
    if t_n11 >= deadline {
        println!("Search deadline reached before length 11; no codebook written.");
        return;
    }
    let g11 = Graph::build(11);
    let n11_budget = if calibrate_only {
        budget_secs.min(10.0)
    } else {
        (budget_secs * 0.08).min(15.0)
    };
    let half_deadline = deadline.min(t_n11 + Duration::from_secs_f64(n11_budget));
    let halves_11 = collect_n11_halves(&g11, seed ^ 0x11, half_deadline);
    println!(
        "=== Calibration n=11 (2dc.2048): found {} distinct size-24 codes in {:.2}s ===",
        halves_11.len(),
        t_n11.elapsed().as_secs_f64()
    );
    if calibrate_only {
        return;
    }

    let t_g12 = Instant::now();
    if t_g12 >= deadline {
        println!("Search deadline reached before length 12; no codebook written.");
        return;
    }
    let g12 = Graph::build(12);
    let min_deg = *g12.deg.iter().min().unwrap();
    let max_deg = *g12.deg.iter().max().unwrap();
    let avg_deg = g12.deg.iter().sum::<usize>() as f64 / g12.n_verts as f64;
    println!(
        "=== Built G_12 (V=4096): deg min={}, avg={:.1}, max={} in {:.3}s ===",
        min_deg,
        avg_deg,
        max_deg,
        t_g12.elapsed().as_secs_f64()
    );

    let mut global_best: Vec<usize> = Vec::new();
    let mut best_regime = String::new();

    // Regime A: Varying fixed n=11 size-24 halves (plus bit-reversed halves before appending 0)
    let mut completed_halves = 0;
    let mut fixed_half_best = 0usize;
    let mut fixed_half_seeds: Vec<Vec<usize>> = Vec::new();
    let mut half_variants: BTreeSet<Vec<usize>> = BTreeSet::new();
    for h in &halves_11 {
        half_variants.insert(h.clone());
        let mut rev: Vec<usize> = h
            .iter()
            .map(|&v| {
                let mut r = 0usize;
                for b in 0..11 {
                    if (v >> b) & 1 == 1 {
                        r |= 1 << (10 - b);
                    }
                }
                r
            })
            .collect();
        rev.sort_unstable();
        half_variants.insert(rev);
    }
    for h in &half_variants {
        if Instant::now() >= deadline {
            break;
        }
        let (sol, complete) = solve_opposite_half(&g12, h, deadline, 5_000_000);
        if complete {
            completed_halves += 1;
        }
        if sol.len() > fixed_half_best {
            fixed_half_best = sol.len();
        }
        update_global_best(
            &g12,
            &sol,
            &format!("Regime A fixed-half ({} words)", sol.len()),
            &mut global_best,
            &mut best_regime,
        );
        fixed_half_seeds.push(sol);
    }
    println!(
        "Regime A (varying fixed n=11 size-24 half): searched {} of {} half variants, {} completed exactly, largest incumbent = {}",
        fixed_half_seeds.len(),
        half_variants.len(),
        completed_halves,
        fixed_half_best
    );

    let t_b = Instant::now();
    let deadline_b = t_b + deadline.saturating_duration_since(t_b).mul_f64(0.40);
    let mut rng = Rng::new(seed ^ 0x12);
    let mut ls = LocalState::new(&g12, deadline_b);
    let mut tabu = vec![0usize; g12.n_verts];
    let mut step = 0usize;

    // Regime B: Releasing words from fixed halves and from both halves + Bipartite Crossover
    let mut b_best = 0usize;
    let mut b_iters = 0usize;
    let mut b_pool: Vec<Vec<usize>> = fixed_half_seeds;
    let mut b_seen: BTreeSet<Vec<usize>> = BTreeSet::new();
    while Instant::now() < deadline_b && !b_pool.is_empty() {
        b_iters += 1;
        if b_pool.len() >= 2 && rng.next_usize(3) == 0 {
            let p1 = &b_pool[rng.next_usize(b_pool.len())];
            let p2 = &b_pool[rng.next_usize(b_pool.len())];
            let child = bipartite_crossover(&g12, p1, p2, &mut rng);
            ls.reset(&child);
        } else {
            let base = &b_pool[rng.next_usize(b_pool.len())];
            ls.reset(base);
            let mut h0: Vec<usize> = ls.set_vec.iter().copied().filter(|&v| (v & 1) == 0).collect();
            let mut h1: Vec<usize> = ls.set_vec.iter().copied().filter(|&v| (v & 1) == 1).collect();
            for i in (1..h0.len()).rev() {
                let j = rng.next_usize(i + 1);
                h0.swap(i, j);
            }
            for i in (1..h1.len()).rev() {
                let j = rng.next_usize(i + 1);
                h1.swap(i, j);
            }
            let d0 = (1 + rng.next_usize(6)).min(h0.len());
            let d1 = (1 + rng.next_usize(6)).min(h1.len());
            for &u in &h0[..d0] {
                ls.remove_vertex_raw(u);
            }
            for &u in &h1[..d1] {
                ls.remove_vertex_raw(u);
            }
        }
        let mut best_local = ls.set_vec.clone();
        ls.plateau_search(&mut rng, 400, &mut tabu, &mut step, &mut best_local);
        ls.force_push(&mut rng);
        ls.plateau_search(&mut rng, 200, &mut tabu, &mut step, &mut best_local);
        for k in [8, 10, 12] {
            if Instant::now() >= deadline_b {
                break;
            }
            ls.exact_lns_step(&mut rng, k, 150_000, &mut best_local);
        }
        while ls.try_two_three_improve(&mut rng) {}
        if ls.set_vec.len() > best_local.len() {
            best_local = ls.set_vec.clone();
        }
        update_global_best(
            &g12,
            &best_local,
            &format!("Regime B release-both-halves (iter {})", b_iters),
            &mut global_best,
            &mut best_regime,
        );
        if best_local.len() > b_best {
            b_best = best_local.len();
            println!(
                "  [Regime B iter {} | {:.1}s] new best = {}",
                b_iters,
                t_b.elapsed().as_secs_f64(),
                b_best
            );
        }
        if best_local.len() >= b_best.saturating_sub(1) && best_local.len() >= 34 {
            let mut key = best_local.clone();
            key.sort_unstable();
            if b_seen.insert(key) {
                if b_pool.len() < 128 {
                    b_pool.push(best_local);
                } else {
                    let slot = rng.next_usize(b_pool.len());
                    if best_local.len() >= b_pool[slot].len() {
                        b_pool[slot] = best_local;
                    }
                }
            }
        }
    }
    println!(
        "Regime B (release from fixed/both halves + crossover): {} iters in {:.2}s, best size = {}",
        b_iters,
        t_b.elapsed().as_secs_f64(),
        b_best
    );

    // Regime C: Unrestricted starts + Evolutionary König Bipartite Crossover + Exact-LNS + (2,3)-swaps
    let t_c = Instant::now();
    ls.deadline = deadline;
    let mut c_best = 0usize;
    let mut c_starts = 0usize;
    let mut elite: Vec<Vec<usize>> = Vec::new();
    let mut elite_seen: BTreeSet<Vec<usize>> = BTreeSet::new();
    if global_best.len() >= 35 {
        let mut s = global_best.clone();
        s.sort_unstable();
        elite_seen.insert(s);
        elite.push(global_best.clone());
    }

    while Instant::now() < deadline {
        c_starts += 1;
        if elite.len() >= 2 && rng.next_usize(3) == 0 {
            let p1 = &elite[rng.next_usize(elite.len())];
            let p2 = &elite[rng.next_usize(elite.len())];
            let child = bipartite_crossover(&g12, p1, p2, &mut rng);
            ls.reset(&child);
            if rng.next_usize(2) == 0 {
                ls.force_push(&mut rng);
            }
        } else if !elite.is_empty() && rng.next_usize(2) == 0 {
            let base = &elite[rng.next_usize(elite.len())];
            ls.reset(base);
            if rng.next_usize(2) == 0 {
                for _ in 0..(1 + rng.next_usize(3)) {
                    ls.force_push(&mut rng);
                }
            } else {
                let k_pert = 5 + rng.next_usize(10);
                let mut s_copy = ls.set_vec.clone();
                for i in (1..s_copy.len()).rev() {
                    let j = rng.next_usize(i + 1);
                    s_copy.swap(i, j);
                }
                for &u in s_copy.iter().take(k_pert.min(s_copy.len())) {
                    ls.remove_vertex_raw(u);
                }
            }
        } else {
            ls.reset(&[]);
            let n_seed = rng.next_usize(4);
            for _ in 0..n_seed {
                let mut free = Vec::new();
                for v in 0..g12.n_verts {
                    if !ls.in_set.test(v) && ls.conf_count[v] == 0 {
                        free.push(v);
                    }
                }
                if free.is_empty() {
                    break;
                }
                let pick = free[rng.next_usize(free.len())];
                ls.add_vertex_raw(pick);
            }
            ls.greedy_fill(&mut rng, c_starts % 2 == 0);
        }

        let mut best_local = ls.set_vec.clone();
        ls.plateau_search(&mut rng, 600, &mut tabu, &mut step, &mut best_local);
        while ls.try_two_three_improve(&mut rng) {}
        for k in [8, 10, 12, 14] {
            if Instant::now() >= deadline {
                break;
            }
            if ls.exact_lns_step(&mut rng, k, 200_000, &mut best_local) {
                while ls.scan_one_tight_and_try_12(&mut rng) {}
                while ls.try_two_three_improve(&mut rng) {}
            }
        }
        if ls.set_vec.len() > best_local.len() {
            best_local = ls.set_vec.clone();
        }

        for v in 0..g12.n_verts {
            if !ls.in_set.test(v) && ls.conf_count[v] == 1 {
                ls.penalties[v] = ls.penalties[v].saturating_add(1).min(100);
            }
        }

        update_global_best(
            &g12,
            &best_local,
            &format!("Regime C unrestricted (start {})", c_starts),
            &mut global_best,
            &mut best_regime,
        );
        if best_local.len() > c_best {
            c_best = best_local.len();
            println!(
                "  [Regime C start {} | {:.1}s] new best = {}",
                c_starts,
                t_c.elapsed().as_secs_f64(),
                c_best
            );
        }
        if best_local.len() >= c_best.saturating_sub(1) && best_local.len() >= 35 {
            let mut key = best_local.clone();
            key.sort_unstable();
            if elite_seen.insert(key) {
                if elite.len() < 128 {
                    elite.push(best_local);
                } else {
                    let slot = rng.next_usize(elite.len());
                    if best_local.len() >= elite[slot].len() {
                        elite[slot] = best_local;
                    }
                }
            }
        }
    }

    println!(
        "Regime C (unrestricted starts + König crossover): {} starts in {:.2}s, best size = {}",
        c_starts,
        t_c.elapsed().as_secs_f64(),
        c_best
    );

    if global_best.is_empty() {
        println!("No length-12 incumbent; no codebook written.");
        return;
    }
    global_best.sort_unstable();
    assert!(verify_independent(&g12, &global_best));
    let mut out_lines = Vec::new();
    out_lines.push(format!(
        "# n=12 two-deletion codebook: {} words (seed={}, budget_secs={:.1}, best_regime={})",
        global_best.len(),
        seed,
        budget_secs,
        best_regime
    ));
    for &v in &global_best {
        out_lines.push(fmt_word(v, 12));
    }
    fs::write(&out_path, out_lines.join("\n") + "\n").expect("write codebook");
    println!(
        "FINAL: best n=12 codebook has {} words (written to {}), regime: {}",
        global_best.len(),
        out_path,
        best_regime
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reports_node_limited_calibration_and_fixed_half() {
        let deadline = Instant::now() + Duration::from_secs(5);
        calibrate_small(3, deadline, 1);
        calibrate_small(3, deadline, 100);
        let graph = Graph::build(4);
        let (incumbent, complete) = solve_opposite_half(&graph, &[0], deadline, 1);
        assert!(!complete);
        assert!(verify_independent(&graph, &incumbent));
        let (optimum, complete) = solve_opposite_half(&graph, &[0], deadline, 100);
        assert!(complete);
        assert_eq!(optimum.len(), 2);
    }
}
