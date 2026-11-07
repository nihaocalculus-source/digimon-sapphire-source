#!/bin/zsh
set -eu
cd -- "${0:A:h}"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
test_dir=$(mktemp -d "${TMPDIR:-/tmp}/digimon-tests.XXXXXX")
trap 'rm -rf "$test_dir"' EXIT
node --test campaign/test.mjs campaign/test-routes.mjs
cc -std=c99 -Wall -Wextra -Werror -Icampaign/tests/stubs -Idevelopment/source/include development/source/src/digimon_campaign.c development/source/src/digimon_rewards.c campaign/tests/test_campaign_native.c -o "$test_dir/campaign"
"$test_dir/campaign"
cc -std=c99 -Wall -Wextra -Werror -Idevelopment/source/include development/source/src/digimon_trail.c campaign/tests/test_follower_trail.c -o "$test_dir/follower"
"$test_dir/follower"

for edition in RUBY SAPPHIRE; do
  cc -std=c99 -Wall -Wextra -Werror -D"$edition" -Icampaign/tests/stubs -Idevelopment/source/include development/source/src/digimon_rewards.c campaign/tests/test_rewards_native.c -o "$test_dir/rewards"
  "$test_dir/rewards"
done
cc -std=c99 -Wall -Wextra -Werror -Icampaign/tests/finale-stubs -Icampaign/tests/stubs -Idevelopment/source/include development/source/src/digimon_finale.c campaign/tests/test_finale_native.c -o "$test_dir/finale"
"$test_dir/finale"
