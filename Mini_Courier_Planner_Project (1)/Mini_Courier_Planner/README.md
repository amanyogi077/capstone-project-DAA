# Mini-Courier Planner

**Course:** Design & Analysis of Algorithms (ETCCDA302)  
**University:** K.R. Mangalam University  
**Project type:** Individual Python coding-based capstone

## 1. Problem statement
Build a prototype that receives parcels and delivery points, prioritizes parcels, selects a feasible set for a limited-capacity courier box, calculates shortest paths, and creates an approximate delivery tour.

## 2. Algorithms used
| Component | Algorithm | Purpose | Time complexity |
|---|---|---|---|
| Parcel ordering | Merge Sort | Sort by priority, then deadline | O(n log n) |
| Packing | 0/1 Knapsack DP | Maximize total parcel value within capacity | O(nC) time, O(nC) space in this table-based implementation |
| Road navigation | Dijkstra with binary heap | Single-source shortest paths | O((V+E) log V) |
| Multi-stop tour | Nearest Neighbor | Approximate visit order | O(k²), after distance table is available |

Here `n` = number of parcels, `C` = capacity in tenths of kg, `V` = graph vertices, `E` = graph edges, and `k` = number of unique delivery points.

## 3. Requirements
- Python 3.9 or later
- No third-party Python packages are required for the program.
- The runtime chart in `outputs/` was created separately for the report.

## 4. Folder structure
```
Mini_Courier_Planner/
├── courier_planner.py
├── README.md
├── data/
│   ├── parcels.csv
│   └── roads.csv
└── outputs/
    ├── sample_output.txt
    └── runtime_comparison.png
```

## 5. Run the project
Open a terminal in this folder and run:

```bash
python courier_planner.py
```

Change box capacity:

```bash
python courier_planner.py --capacity 8
```

Use your own CSV files:

```bash
python courier_planner.py --parcels data/parcels.csv --edges data/roads.csv --capacity 10 --depot Warehouse
```

## 6. Input formats
### parcels.csv
Columns: `parcel_id,destination,weight,priority,deadline,value`

- `parcel_id`: unique parcel label
- `destination`: graph node name
- `weight`: parcel weight in kg
- `priority`: High, Medium, or Low
- `deadline`: date/time text used for ordering within equal priority
- `value`: numerical benefit used by Knapsack. The sample uses 100/60/30 for High/Medium/Low.

### roads.csv
Columns: `from,to,distance`

Each row is a two-way road. Distances must be non-negative and use the same unit (sample: kilometres). The graph is undirected.

## 7. How the system works
1. Read parcel and road CSV files.
2. Merge Sort orders parcels by High, Medium, Low priority, then earlier deadline.
3. 0/1 Knapsack selects the combination with maximum total value that fits the capacity. Each parcel is either selected once or not selected.
4. Dijkstra computes shortest road distances from each graph node.
5. Nearest Neighbor repeatedly visits the nearest unvisited selected destination, then returns to the warehouse.
6. Print selected parcels, shortest paths, route, packing utilization, and total route length.

## 8. Important assumptions and limitations
- This is an educational prototype, not a live navigation service.
- Road distances are fixed sample values; real traffic, road closures, and time-dependent travel are not modeled.
- Dijkstra requires non-negative edge weights.
- Nearest Neighbor is a heuristic and does **not** guarantee the globally shortest TSP tour.
- The Knapsack objective is the supplied `value` field. In the sample, value represents priority score; actual business value could be substituted.
- The planner first optimizes parcel selection and then plans a route for the selected unique destinations. It does not jointly optimize packing and route distance.
- The nearest-neighbor tour includes a return to the warehouse.

## 9. Testing
Run the default sample, then change `--capacity` to 6 and 12. Confirm:
- Selected weight never exceeds capacity.
- Only High/Medium/Low priorities are accepted.
- The shortest path distances are non-negative.
- The tour starts and ends at the warehouse.
- Every selected destination appears in the tour.

## 10. Complexity discussion
- Merge Sort: O(n log n) time and O(n) auxiliary space.
- Knapsack DP: O(nC) time and O(nC) space; pseudo-polynomial in capacity.
- Dijkstra: O((V+E) log V) per source with a binary heap; this implementation runs it from every graph node, so all-pairs preparation is O(V(V+E) log V).
- Nearest Neighbor: O(k²) for k delivery points when distances are already available.

## 11. Future improvements
- Use road-network data and live traffic.
- Add a graphical interface and map visualization.
- Improve the TSP tour using 2-opt or other local-search methods.
- Use a one-dimensional Knapsack DP array to reduce memory to O(C).
- Add unit tests and export delivery plans to CSV/PDF.
