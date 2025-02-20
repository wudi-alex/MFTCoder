"""
# @author Chaoyu Chen
# @date 2023/6/19

"""

import os

os.environ['TRANSFORMERS_CACHE'] = '/datasets/Large_Language_Models'

import sys
import time
import shutil
import torch
import transformers
import argparse

sys.path.append("..")
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel
from peft import LoraConfig, get_peft_model
from peft import PeftModel


# from model_mapping import MODEL_SPECIAL_TOKENS


def main():
    parser = argparse.ArgumentParser(description='Script to merge models.')

    # Define arguments
    parser.add_argument('--model_path', type=str, required=True,
                        help='Path to the model')
    parser.add_argument('--lora_adapter', type=str, required=True,
                        help='Path to the LoRA adapter')
    parser.add_argument('--save_path', type=str, default='./merged_models/',
                        help='Path to save the new merged model')
    parser.add_argument('--model_type', type=str, default='llama',
                        help='Type of the model (e.g., llama)')

    # Parse arguments
    args = parser.parse_args()

    # Accessing arguments
    model_path = args.model_path
    lora_adapter = args.lora_adapter
    save_path = args.save_path
    model_type = args.model_type

    t0 = time.time()
    config = {"model_type": model_type}
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    base_model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        return_dict=True,
        device_map="auto"
    )
    print(base_model)

    # DEAL with eos_token_id and pad_token_id
    # eos_token = MODEL_SPECIAL_TOKENS[config['model_type']]['eos_token']
    # pad_token = MODEL_SPECIAL_TOKENS[config['model_type']]['pad_token']
    eos_token = '</s>'
    pad_token = '<unk>'
    base_model.config.eos_token = eos_token
    base_model.config.pad_token = pad_token
    base_model.config.eos_token_id = tokenizer.convert_tokens_to_ids(eos_token)
    base_model.config.pad_token_id = tokenizer.convert_tokens_to_ids(pad_token)
    print(f"Finetuned eos_token: {eos_token}, eos_token_id: {tokenizer.convert_tokens_to_ids(eos_token)}")
    print(f"Finetuned pad_token: {pad_token}, pad_token_id: {tokenizer.convert_tokens_to_ids(pad_token)}")

    # merge, save model and tokenizer
    model_to_merge = PeftModel.from_pretrained(base_model, lora_adapter)
    merged_model = model_to_merge.merge_and_unload()
    print(merged_model.config)
    merged_model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    print(f"Merge finised: {save_path} saved, Cost {time.time() - t0:.2f}s")


if __name__ == '__main__':
    main()
