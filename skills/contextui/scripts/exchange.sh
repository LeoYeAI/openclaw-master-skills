#!/bin/bash
# ContextUI Exchange CLI helper
# Usage: exchange.sh <command> [args]
#
# Requires: CONTEXTUI_API_KEY environment variable
#
# Commands:
#   search <query>              Search workflows
#   get <id>                    Get workflow details
#   category <category>         Browse by category
#   download <id>               Get download URLs
#   comments <listing_id>       Get comments
#   comment <listing_id> <body> Post a comment
#   like <listing_id>           Toggle like
#   my-workflows                List your workflows
#   my-downloads                List your downloads
#   delete <id>                 Soft-delete your listing
#   hard-delete <id>            Permanently delete (must be soft-deleted first)

set -e

BASE="https://contextui.ai/.netlify/functions"
KEY="${CONTEXTUI_API_KEY:?Set CONTEXTUI_API_KEY environment variable}"

case "$1" in
  search)
    [ -z "$2" ] && echo "Usage: exchange.sh search <query>" && exit 1
    curl -s -H "Authorization: Bearer $KEY" "$BASE/marketplace?search=$(echo "${@:2}" | sed 's/ /%20/g')"
    ;;
  get)
    [ -z "$2" ] && echo "Usage: exchange.sh get <uuid>" && exit 1
    curl -s -H "Authorization: Bearer $KEY" "$BASE/marketplace?id=$2"
    ;;
  category)
    [ -z "$2" ] && echo "Usage: exchange.sh category <category>" && exit 1
    curl -s -H "Authorization: Bearer $KEY" "$BASE/marketplace?category=$2"
    ;;
  download)
    [ -z "$2" ] && echo "Usage: exchange.sh download <uuid>" && exit 1
    curl -s -H "Authorization: Bearer $KEY" "$BASE/marketplace-download?id=$2"
    ;;
  comments)
    [ -z "$2" ] && echo "Usage: exchange.sh comments <listing_id>" && exit 1
    curl -s -H "Authorization: Bearer $KEY" "$BASE/marketplace-comments?listingId=$2"
    ;;
  comment)
    [ -z "$3" ] && echo "Usage: exchange.sh comment <listing_id> <body>" && exit 1
    curl -s -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
      -d "{\"listingId\":\"$2\",\"body\":\"$3\"}" "$BASE/marketplace-comments"
    ;;
  like)
    [ -z "$2" ] && echo "Usage: exchange.sh like <listing_id>" && exit 1
    curl -s -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
      -d "{\"listingId\":\"$2\"}" "$BASE/marketplace-like"
    ;;
  my-workflows)
    curl -s -H "Authorization: Bearer $KEY" "$BASE/marketplace-my-workflows"
    ;;
  my-downloads)
    curl -s -H "Authorization: Bearer $KEY" "$BASE/marketplace-my-downloads"
    ;;
  delete)
    [ -z "$2" ] && echo "Usage: exchange.sh delete <uuid>" && exit 1
    curl -s -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
      -d "{\"listingId\":\"$2\"}" "$BASE/marketplace-delete"
    ;;
  hard-delete)
    [ -z "$2" ] && echo "Usage: exchange.sh hard-delete <uuid>" && exit 1
    curl -s -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
      -d "{\"listingId\":\"$2\",\"hardDelete\":true}" "$BASE/marketplace-delete"
    ;;
  *)
    echo "ContextUI Exchange CLI"
    echo ""
    echo "Usage: exchange.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  search <query>              Search workflows"
    echo "  get <uuid>                  Get workflow details"
    echo "  category <category>         Browse by category"
    echo "  download <uuid>             Get download URLs"
    echo "  comments <listing_id>       Get comments"
    echo "  comment <listing_id> <body> Post a comment"
    echo "  like <listing_id>           Toggle like"
    echo "  my-workflows                List your workflows"
    echo "  my-downloads                List your downloads"
    echo "  delete <uuid>               Soft-delete your listing"
    echo "  hard-delete <uuid>          Permanently delete"
    echo ""
    echo "Categories: gen_ai, developer_tools, creative_tools, productivity,"
    echo "            games, data_tools, file_utilities, image_processing,"
    echo "            video_processing, llm"
    echo ""
    echo "Upload workflows via the 2-step API (see SKILL.md):"
    echo "  1. POST marketplace-upload-init (get presigned S3 URLs)"
    echo "  2. PUT files to S3"
    echo "  3. POST marketplace-upload-complete (create listing)"
    exit 1
    ;;
esac
