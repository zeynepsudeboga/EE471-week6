import os
os.environ["TORCH_HOME"] = "."  # keep downloaded weights inside the project, so they get baked into the image

import json
from datetime import datetime

import torch
from cog import BaseRunner, Input, Path
from PIL import Image
from torchvision import models

# Same pre-trained model as the Cog getting-started guide (ResNet50 trained on ImageNet)
WEIGHTS = models.ResNet50_Weights.IMAGENET1K_V1

# ImageNet has five domestic-cat classes; these are the "cat kinds" we report
CAT_CLASSES = ["tabby", "tiger cat", "Persian cat", "Siamese cat", "Egyptian cat"]

LOG_FILE = "/tmp/predictions.log"  # read live from inside the container with: tail -f /tmp/predictions.log


class Runner(BaseRunner):
    def setup(self):
        """Runs once when the container starts: load the model into memory."""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = models.resnet50(weights=WEIGHTS).to(self.device)
        self.model.eval()
        self.categories = WEIGHTS.meta["categories"]
        # match names whether the label list uses spaces or underscores ("tiger cat" / "tiger_cat")
        normalized = [c.replace("_", " ").lower() for c in self.categories]
        self.cat_ids = [normalized.index(name.lower()) for name in CAT_CLASSES]
        open(LOG_FILE, "a").close()  # create the log file now, so "tail -f" works before the first request

    def run(self, image: Path = Input(description="Photo of a cat")) -> dict:
        """Runs for every request: classify one image."""
        img = Image.open(image).convert("RGB")
        with torch.no_grad():
            probs = self.model(WEIGHTS.transforms()(img).unsqueeze(0).to(self.device))[0].softmax(0)

        # How much of the model's belief goes to cat classes at all
        cat_total = probs[self.cat_ids].sum().item()
        # Share of each cat kind among the cat classes (sums to 1)
        breeds = {name: probs[i].item() / cat_total for name, i in zip(CAT_CLASSES, self.cat_ids)}
        breeds = dict(sorted(breeds.items(), key=lambda kv: kv[1], reverse=True))
        top = probs.topk(3)
        result = {
            "is_cat": cat_total > 0.5,
            "cat_confidence": round(cat_total, 4),
            "best_guess": next(iter(breeds)),
            "breeds": {k: round(v, 4) for k, v in breeds.items()},
            "top3_imagenet": {self.categories[i]: round(p.item(), 4) for p, i in zip(*top)},
        }

        line = f"{datetime.now():%H:%M:%S} prediction: {json.dumps(result)}"
        print(line, flush=True)            # visible in: docker logs -f
        with open(LOG_FILE, "a") as f:     # visible from inside the container
            f.write(line + "\n")
        return result
