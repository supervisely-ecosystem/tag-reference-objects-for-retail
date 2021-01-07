from collections import defaultdict
import supervisely_lib as sly
import globals as ag

data = defaultdict(list)


def index_existing():
    global data
    data = defaultdict(list)

    progress = sly.Progress("Collecting existing references", ag.project.items_count, ext_logger=ag.app.logger, need_info_log=True)
    for dataset_info in ag.api.dataset.get_list(ag.project.id):
        images_infos = ag.api.image.get_list(dataset_info.id)
        for batch in sly.batched(images_infos):
            ids = [info.id for info in batch]
            anns_infos = ag.api.annotation.download_batch(dataset_info.id, ids)
            anns = [sly.Annotation.from_json(info.annotation, ag.meta) for info in anns_infos]
            for ann, image_info in zip(anns, batch):
                if ag.field_name not in image_info.meta:
                    ag.app.logger.warn(f"Field \"{ag.field_name}\" not found in metadata: "
                                       f"image \"{image_info.name}\"; id={image_info.id}")
                    continue
                field_value = image_info.meta[ag.field_name]
                for label in ann.labels:
                    label: sly.Label
                    if label.obj_class.name != ag.target_class_name:
                        continue
                    if label.tags.get(ag.reference_tag_name) is not None:
                        data[field_value].append({"image_info": image_info, "label": label})
            progress.iters_done_report(len(batch))
            break #@TODO: for debug
        break  # @TODO: for debug
