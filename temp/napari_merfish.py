import napari_spatialdata.constants.config
from napari_spatialdata import Interactive
napari_spatialdata.constants.config.PROJECT_2_5D_SHAPES_TO_2D = False
napari_spatialdata.constants.config.PROJECT_3D_POINTS_TO_2D = False
import spatialdata as sd
from pathlib import Path


out_path = Path(__file__).parent.parent / "data"
sdata_path = out_path / "merfish_mouse_ileum.sdata.zarr"

sdata = sd.read_zarr(sdata_path)


# Interactive(sdata)

##
# subset the data
sdata_small = sd.bounding_box_query(
    sdata,
    axes=("x", "y", "z"),
    min_coordinate=[4000, 0, -10],
    max_coordinate=[5000, 1500, 200],
    target_coordinate_system="global",
)

transformation = sd.transformations.get_transformation(sdata_small["stains"])
translation_vector = transformation.to_affine_matrix(
    input_axes=("x", "y", "z"), output_axes=("x", "y", "z")
)[:3, 3]
translation = sd.transformations.Translation(translation_vector, axes=("x", "y", "z"))
for _, element_name, _ in sdata_small.gen_spatial_elements():
    old_transformation = sd.transformations.get_transformation(
        sdata_small[element_name]
    )
    sequence = sd.transformations.Sequence([old_transformation, translation.inverse()])
    sd.transformations.set_transformation(
        sdata_small[element_name],
        transformation=sequence,
        to_coordinate_system="global",
    )
    if sd.models.get_model(sdata_small[element_name]) not in (
        sd.models.Image3DModel,
        sd.models.Labels3DModel,
    ):
        transformed = sd.transform(sdata_small[element_name], to_coordinate_system="global")
        sdata_small[element_name] = transformed

sdata = sdata_small