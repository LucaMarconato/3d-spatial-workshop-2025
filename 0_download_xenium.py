##
import lamindb as ln
import pickle
import ovrlpy
from napari_spatialdata import Interactive  # noqa: F401
import spatialdata as sd
import matplotlib.pyplot as plt
import vedo
import numpy as np

# we will download the dataset "Xenium FFPE Healthy Human Breast", provided from 10x Genomics https://www.10xgenomics.com/datasets/ffpe-human-breast-with-custom-add-on-panel-1-standard
#
# spatialdata-db link:
# https://lamin.ai/scverse/spatialdata-db/artifacts?filter[and][0][or][0][is_latest][eq]=true&filter[and][1][or][0][branch.name][eq]=main&filter[and][2][or][0][schema.name][eq]=Xenium
artifact = ln.Artifact.get("Uj7J4jjgzHw0lcm80001")
gb = artifact.size / 1_000_000_000
print(f"{gb:.2f} GB")

##
artifact.cache()
f = artifact._cache_path

##


sdata = sd.read_zarr(str(f))
print(sdata)
#
# Interactive(sdata)

##

transcripts = sdata['transcripts'].compute()
transcripts['gene'] = transcripts['feature_name']

##
# dataset = ovrlpy.Ovrlp(
#     transcripts,
#     n_components=20,
#     n_workers=4,
# )
# dataset.analyse()

#
# with open("data/analysis.pickle", "wb") as file:
#     pickle.dump(dataset, file)

##
with open("data/analysis.pickle", "rb") as file:
    dataset = pickle.load(file)

##

# ovrlpy.plot_pseudocells(dataset)
# plt.show()

##
# fig = ovrlpy.plot_signal_integrity(dataset, signal_threshold=3)
# plt.show()

##
doublets = dataset.detect_doublets(min_signal=3, integrity_sigma=2)

##
# fig, ax = plt.subplots()
# _scatter = ax.scatter(
#     doublets["x"], doublets["y"], c=doublets["integrity"], s=0.2, cmap="viridis"
# )
# _ = ax.set_aspect("equal")
# _ = fig.colorbar(_scatter, ax=ax)
# plt.show()

##
x, y = doublets["x", "y"].row(0)
_ = ovrlpy.plot_region_of_interest(dataset, x, y, window_size=60)
# plt.show()

##
vedo.settings.default_backend = 'k3d'
window_transcripts = dataset.subset_transcripts(x, y, window_size=30)
_, rgb = dataset.transform_transcripts(window_transcripts, gene_key="gene")

list_of_points = window_transcripts[['x', 'y', 'z']].to_pandas().values.tolist()
vedo_points = vedo.Points(list_of_points, r=4)

# vedo_points.pointdata["gene"] = window_transcripts['gene'].to_pandas().cat.codes
# vedo_points.cmap('jet', 'gene')
# vedo_points.pointcolors = (np.array(rgb) * 255).astype(np.uint8)
vedo_points.pointcolors = [[100, 100, 100, 100]] * len(rgb)

# vedo_points.pointdata["gene"] = np.zeros(len(rgb))

# Then use cmap to map it to a colormap
# vedo_points.cmap('viridis', 'gene')

# window_transcripts.columns
vedo.show(vedo_points)